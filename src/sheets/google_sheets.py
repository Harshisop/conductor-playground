import csv
import json
import logging
import os
from pathlib import Path

import gspread

from src.config_loader import GoogleSheetsConfig
from src.models import JobListing, UserConfig

logger = logging.getLogger(__name__)

JOB_URL_COL_INDEX = 4  # 1-based: "Job URL" is the 4th column
MAX_USERS = 5


def get_client(config: GoogleSheetsConfig) -> gspread.Client | None:
    creds_json = os.environ.get(config.credentials_env_var)
    if not creds_json:
        logger.error(f"Environment variable '{config.credentials_env_var}' not set")
        return None

    try:
        creds = json.loads(creds_json)
        return gspread.service_account_from_dict(creds)
    except Exception as e:
        logger.error(f"Google Sheets auth failed: {e}")
        return None


def get_spreadsheet(config: GoogleSheetsConfig) -> gspread.Spreadsheet | None:
    client = get_client(config)
    if client is None:
        return None

    try:
        return client.open(config.spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        logger.error(f"Spreadsheet '{config.spreadsheet_name}' not found. "
                     "Make sure it exists and is shared with the service account.")
        return None


def read_users(config: GoogleSheetsConfig) -> list[UserConfig]:
    spreadsheet = get_spreadsheet(config)
    if spreadsheet is None:
        return []

    try:
        worksheet = spreadsheet.worksheet("Users")
    except gspread.WorksheetNotFound:
        logger.info("No 'Users' worksheet found — falling back to config.yaml")
        return []

    rows = worksheet.get_all_values()
    if len(rows) <= 1:  # Only header or empty
        logger.info("No users registered — falling back to config.yaml")
        return []

    users = []
    for row in rows[1:]:  # Skip header
        if len(row) >= 5 and row[0].strip():
            try:
                users.append(UserConfig.from_sheet_row(row))
            except Exception as e:
                logger.warning(f"Skipping invalid user row: {e}")

        if len(users) >= MAX_USERS:
            break

    logger.info(f"Found {len(users)} registered user(s)")
    return users


def get_existing_urls(worksheet: gspread.Worksheet) -> set[str]:
    try:
        all_values = worksheet.col_values(JOB_URL_COL_INDEX)
        return set(all_values[1:]) if len(all_values) > 1 else set()
    except Exception as e:
        logger.warning(f"Could not read existing URLs: {e}")
        return set()


def push_jobs_for_user(
    config: GoogleSheetsConfig,
    user_name: str,
    jobs: list[JobListing],
) -> tuple[bool, set[str]]:
    """Push jobs to a user-specific worksheet tab. Returns (success, existing_urls)."""
    spreadsheet = get_spreadsheet(config)
    if spreadsheet is None:
        return False, set()

    try:
        worksheet = spreadsheet.worksheet(user_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(user_name, rows=1000, cols=20)

    # Write headers if sheet is empty
    existing_data = worksheet.get_all_values()
    if not existing_data:
        worksheet.append_row(JobListing.sheet_headers(), value_input_option="USER_ENTERED")

    existing_urls = get_existing_urls(worksheet)

    if not jobs:
        logger.info(f"[{user_name}] No jobs to push")
        return True, existing_urls

    rows = [job.to_row() for job in jobs]
    worksheet.append_rows(rows, value_input_option="USER_ENTERED")
    logger.info(f"[{user_name}] Pushed {len(rows)} jobs")
    return True, existing_urls


def push_jobs(config: GoogleSheetsConfig, jobs: list[JobListing]) -> tuple[bool, set[str]]:
    """Push jobs to the default worksheet (fallback single-user mode)."""
    return push_jobs_for_user(config, config.worksheet_name, jobs)


def save_backup_csv(jobs: list[JobListing], user_name: str = "default", path: str | None = None):
    if path is None:
        path = str(Path(__file__).parent.parent.parent / f"backup_jobs_{user_name}.csv")

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(JobListing.sheet_headers())
        for job in jobs:
            writer.writerow(job.to_row())

    logger.info(f"Backup saved to {path}")
