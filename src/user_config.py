from src.config_loader import SearchConfig, ApiSourcesConfig, RemotiveConfig, HimalayasConfig
from src.models import UserConfig

SOURCE_MAP = {
    "linkedin": "linkedin",
    "indeed": "indeed",
    "google jobs": "google",
    "google": "google",
    "naukri": "naukri",
}

JOB_TYPE_MAP = {
    "full-time": "fulltime",
    "fulltime": "fulltime",
    "part-time": "parttime",
    "parttime": "parttime",
    "contract": "contract",
    "internship": "internship",
}


def user_to_searches(user: UserConfig) -> list[SearchConfig]:
    sites = []
    for s in user.sources:
        mapped = SOURCE_MAP.get(s.lower())
        if mapped:
            sites.append(mapped)
    if not sites:
        sites = ["linkedin", "google"]

    searches = []
    for keyword in user.keywords:
        for location in user.locations:
            for job_type_raw in user.job_types:
                job_type = JOB_TYPE_MAP.get(job_type_raw.lower(), "fulltime")
                is_remote = location.lower() == "remote"

                searches.append(SearchConfig(
                    keywords=keyword,
                    location=location,
                    sites=sites,
                    job_type=job_type,
                    remote_only=is_remote,
                    hours_old=168,
                    results_wanted=50,
                ))

    return searches


def user_to_api_config(user: UserConfig) -> ApiSourcesConfig:
    return ApiSourcesConfig(
        remotive=RemotiveConfig(
            enabled=True,
            categories=["marketing", "sales", "software-dev"],
        ),
        himalayas=HimalayasConfig(
            enabled=True,
            keywords=user.keywords,
        ),
    )
