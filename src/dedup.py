import hashlib
from urllib.parse import urlparse, urlunparse

from src.models import JobListing


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip().lower())
    path = parsed.path.rstrip("/")
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def job_hash(job: JobListing) -> str:
    key = f"{job.title.lower().strip()}|{job.company.lower().strip()}|{job.location.lower().strip()}"
    return hashlib.md5(key.encode()).hexdigest()


def deduplicate(jobs: list[JobListing], existing_urls: set[str] | None = None) -> list[JobListing]:
    if existing_urls is None:
        existing_urls = set()

    seen_urls: set[str] = set()
    seen_hashes: set[str] = set()
    unique: list[JobListing] = []

    normalized_existing = {normalize_url(u) for u in existing_urls}

    for job in jobs:
        norm_url = normalize_url(job.job_url)

        # Skip if already in the Google Sheet
        if norm_url in normalized_existing:
            continue

        # Skip URL duplicates within this batch
        if norm_url in seen_urls:
            continue

        # Skip title+company+location duplicates (cross-site same job)
        h = job_hash(job)
        if h in seen_hashes:
            continue

        seen_urls.add(norm_url)
        seen_hashes.add(h)
        unique.append(job)

    return unique
