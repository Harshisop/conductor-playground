import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class SearchConfig(BaseModel):
    keywords: str
    location: str = ""
    sites: list[str] = ["linkedin", "indeed", "google"]
    job_type: str = "fulltime"
    remote_only: bool = False
    hours_old: int = 72
    results_wanted: int = 50


class RemotiveConfig(BaseModel):
    enabled: bool = True
    categories: list[str] = ["software-dev"]


class HimalayasConfig(BaseModel):
    enabled: bool = True
    keywords: list[str] = ["software engineer"]


class ApiSourcesConfig(BaseModel):
    remotive: RemotiveConfig = Field(default_factory=RemotiveConfig)
    himalayas: HimalayasConfig = Field(default_factory=HimalayasConfig)


class GoogleSheetsConfig(BaseModel):
    spreadsheet_name: str = "Job Scraper Results"
    worksheet_name: str = "Jobs"
    credentials_env_var: str = "GOOGLE_SHEETS_CREDS_JSON"


class SettingsConfig(BaseModel):
    delay_between_searches: int = 3
    max_retries: int = 2
    deduplicate: bool = True
    log_level: str = "INFO"


class AppConfig(BaseModel):
    searches: list[SearchConfig] = Field(default_factory=list)
    api_sources: ApiSourcesConfig = Field(default_factory=ApiSourcesConfig)
    google_sheets: GoogleSheetsConfig = Field(default_factory=GoogleSheetsConfig)
    settings: SettingsConfig = Field(default_factory=SettingsConfig)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    if config_path is None:
        config_path = str(Path(__file__).parent.parent / "config.yaml")

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    return AppConfig(**raw)
