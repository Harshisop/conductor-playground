import logging
from datetime import date

import requests

from src.models import JobListing

logger = logging.getLogger(__name__)

BASE_URL = "https://himalayas.app/jobs/api"


def scrape(keywords: list[str]) -> list[JobListing]:
    all_jobs: list[JobListing] = []

    for keyword in keywords:
        try:
            resp = requests.get(
                BASE_URL,
                params={"limit": 50, "offset": 0, "search": keyword},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            jobs_list = data.get("jobs", [])
            for item in jobs_list:
                try:
                    def _to_float(val):
                        if val is None:
                            return None
                        try:
                            return float(val)
                        except (ValueError, TypeError):
                            return None

                    job_url = item.get("applicationLink") or item.get("url") or item.get("externalUrl") or ""
                    job = JobListing(
                        title=item.get("title", "Unknown"),
                        company=item.get("companyName", item.get("company_name", "Unknown")),
                        location=item.get("location", "Remote"),
                        job_url=job_url,
                        source="himalayas",
                        date_posted=None,
                        date_scraped=date.today(),
                        job_type=item.get("type"),
                        is_remote=True,
                        salary_min=_to_float(item.get("minSalary")),
                        salary_max=_to_float(item.get("maxSalary")),
                        salary_currency=str(item.get("salaryCurrency", "")) or None,
                        description_snippet=(item.get("description", "") or "")[:300] or None,
                        skills=", ".join(item.get("categories", [])) if item.get("categories") else None,
                        experience_level=item.get("seniority"),
                        company_url=None,
                    )
                    if job.job_url:
                        all_jobs.append(job)
                except Exception as e:
                    logger.warning(f"Himalayas: skipping job: {e}")

            logger.info(f"Himalayas ['{keyword}']: found {len(jobs_list)} jobs")

        except Exception as e:
            logger.error(f"Himalayas ['{keyword}']: failed: {e}")

    return all_jobs
