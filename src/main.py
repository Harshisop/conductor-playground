import logging
import sys
import time

from src.config_loader import load_config
from src.dedup import deduplicate
from src.models import JobListing, UserConfig
from src.scrapers import jobspy_scraper, remotive_api, himalayas_api
from src.sheets.google_sheets import (
    push_jobs,
    push_jobs_for_user,
    read_users,
    save_backup_csv,
)
from src.user_config import user_to_searches, user_to_api_config


def scrape_for_user(user: UserConfig, delay: int) -> list[JobListing]:
    logger = logging.getLogger(__name__)
    all_jobs: list[JobListing] = []

    searches = user_to_searches(user)
    logger.info(f"[{user.name}] Running {len(searches)} search(es)")

    for search in searches:
        jobs = jobspy_scraper.scrape(search, delay=delay)
        all_jobs.extend(jobs)
        time.sleep(delay)

    api = user_to_api_config(user)

    if api.remotive.enabled:
        jobs = remotive_api.scrape(api.remotive.categories)
        all_jobs.extend(jobs)

    if api.himalayas.enabled:
        jobs = himalayas_api.scrape(api.himalayas.keywords)
        all_jobs.extend(jobs)

    logger.info(f"[{user.name}] Total jobs before dedup: {len(all_jobs)}")
    return all_jobs


def run_multi_user(config):
    logger = logging.getLogger(__name__)
    users = read_users(config.google_sheets)

    if not users:
        logger.info("No registered users — falling back to config.yaml single-user mode")
        run_single_user(config)
        return

    any_failure = False
    for user in users:
        logger.info(f"--- Scraping for: {user.name} ---")

        all_jobs = scrape_for_user(user, config.settings.delay_between_searches)

        # Get existing URLs for cross-run dedup
        _, existing_urls = push_jobs_for_user(config.google_sheets, user.name, [])
        unique_jobs = deduplicate(all_jobs, existing_urls)

        logger.info(f"[{user.name}] Unique new jobs: {len(unique_jobs)}")

        if not unique_jobs:
            continue

        success, _ = push_jobs_for_user(config.google_sheets, user.name, unique_jobs)
        if not success:
            logger.warning(f"[{user.name}] Google Sheets push failed — saving backup")
            save_backup_csv(unique_jobs, user_name=user.name)
            any_failure = True
        else:
            logger.info(f"[{user.name}] Added {len(unique_jobs)} new jobs")

    if any_failure:
        sys.exit(1)


def run_single_user(config):
    logger = logging.getLogger(__name__)
    all_jobs: list[JobListing] = []

    for search in config.searches:
        jobs = jobspy_scraper.scrape(search, delay=config.settings.delay_between_searches)
        all_jobs.extend(jobs)
        time.sleep(config.settings.delay_between_searches)

    api = config.api_sources
    if api.remotive.enabled:
        all_jobs.extend(remotive_api.scrape(api.remotive.categories))
    if api.himalayas.enabled:
        all_jobs.extend(himalayas_api.scrape(api.himalayas.keywords))

    logger.info(f"Total jobs before dedup: {len(all_jobs)}")

    _, existing_urls = push_jobs(config.google_sheets, [])
    unique_jobs = deduplicate(all_jobs, existing_urls)

    logger.info(f"Unique new jobs: {len(unique_jobs)}")

    if not unique_jobs:
        logger.info("No new jobs to add")
        return

    success, _ = push_jobs(config.google_sheets, unique_jobs)
    if not success:
        logger.warning("Google Sheets push failed — saving backup")
        save_backup_csv(unique_jobs)
        sys.exit(1)

    logger.info(f"Done! Added {len(unique_jobs)} new jobs.")


def main():
    config = load_config()

    logging.basicConfig(
        level=getattr(logging, config.settings.log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logging.getLogger(__name__).info("Starting job scraper")
    run_multi_user(config)


if __name__ == "__main__":
    main()
