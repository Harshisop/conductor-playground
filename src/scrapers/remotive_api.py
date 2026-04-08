import logging
from datetime import date

import requests

from src.models import JobListing

logger = logging.getLogger(__name__)

BASE_URL = "https://remotive.com/api/remote-jobs"


def scrape(categories: list[str]) -> list[JobListing]:
    all_jobs: list[JobListing] = []

    for category in categories:
        try:
            resp = requests.get(BASE_URL, params={"category": category}, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("jobs", []):
                try:
                    job = JobListing(
                        title=item.get("title", "Unknown"),
                        company=item.get("company_name", "Unknown"),
                        location=item.get("candidate_required_location", "Remote"),
                        job_url=item.get("url", ""),
                        source="remotive",
                        date_posted=None,
                        date_scraped=date.today(),
                        job_type=item.get("job_type"),
                        is_remote=True,
                        salary_min=None,
                        salary_max=None,
                        salary_currency=None,
                        description_snippet=(item.get("description", "") or "")[:300] or None,
                        skills=", ".join(item.get("tags", [])) if item.get("tags") else None,
                        experience_level=None,
                        company_url=item.get("company_logo_url"),
                    )
                    if job.job_url:
                        all_jobs.append(job)
                except Exception as e:
                    logger.warning(f"Remotive: skipping job: {e}")

            logger.info(f"Remotive [{category}]: found {len(data.get('jobs', []))} jobs")

        except Exception as e:
            logger.error(f"Remotive [{category}]: failed: {e}")

    return all_jobs
