import logging
import time
from datetime import date, datetime

import pandas as pd

from src.config_loader import SearchConfig
from src.models import JobListing

logger = logging.getLogger(__name__)


def _parse_date(val) -> date | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()
    try:
        return datetime.fromisoformat(str(val)).date()
    except (ValueError, TypeError):
        return None


def scrape(search: SearchConfig, delay: int = 3) -> list[JobListing]:
    try:
        from jobspy import scrape_jobs
    except ImportError:
        logger.error("python-jobspy not installed. Run: pip install python-jobspy")
        return []

    logger.info(f"JobSpy: searching '{search.keywords}' in '{search.location}' on {search.sites}")

    all_jobs: list[JobListing] = []

    for site in search.sites:
        try:
            df = scrape_jobs(
                site_name=[site],
                search_term=search.keywords,
                location=search.location,
                job_type=search.job_type,
                is_remote=search.remote_only,
                results_wanted=search.results_wanted,
                hours_old=search.hours_old,
                country_indeed="india" if "india" in search.location.lower() else "usa",
            )

            if df is None or df.empty:
                logger.info(f"  {site}: no results")
                continue

            for _, row in df.iterrows():
                try:
                    job_url = str(row.get("job_url", ""))
                    if not job_url:
                        continue

                    # Build location string from available fields
                    loc_parts = [
                        str(row.get("city", "") or ""),
                        str(row.get("state", "") or ""),
                        str(row.get("country", "") or ""),
                    ]
                    location = ", ".join(p for p in loc_parts if p)

                    description = str(row.get("description", "") or "")
                    snippet = description[:300] if description else None

                    job = JobListing(
                        title=str(row.get("title", "Unknown")),
                        company=str(row.get("company", "Unknown")),
                        location=location or search.location,
                        job_url=job_url,
                        source=site,
                        date_posted=_parse_date(row.get("date_posted")),
                        date_scraped=date.today(),
                        job_type=str(row.get("job_type", "")) or None,
                        is_remote=row.get("is_remote"),
                        salary_min=row.get("min_amount"),
                        salary_max=row.get("max_amount"),
                        salary_currency=str(row.get("currency", "")) or None,
                        description_snippet=snippet,
                        skills=str(row.get("skills", "")) or None,
                        experience_level=str(row.get("job_level", "")) or None,
                        company_url=str(row.get("company_url", "")) or None,
                    )
                    all_jobs.append(job)
                except Exception as e:
                    logger.warning(f"  {site}: skipping row: {e}")

            logger.info(f"  {site}: found {len(df)} jobs")

        except Exception as e:
            logger.error(f"  {site}: scraping failed: {e}")

        time.sleep(delay)

    return all_jobs
