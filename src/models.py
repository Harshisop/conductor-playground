from datetime import date
from typing import Optional

from pydantic import BaseModel


class UserConfig(BaseModel):
    name: str
    keywords: list[str]
    locations: list[str]
    sources: list[str]
    job_types: list[str]

    @classmethod
    def from_sheet_row(cls, row: list[str]) -> "UserConfig":
        return cls(
            name=row[0].strip(),
            keywords=[k.strip() for k in row[1].split(",") if k.strip()],
            locations=[l.strip() for l in row[2].split(",") if l.strip()],
            sources=[s.strip() for s in row[3].split(",") if s.strip()],
            job_types=[j.strip() for j in row[4].split(",") if j.strip()],
        )


class JobListing(BaseModel):
    title: str
    company: str
    location: str = ""
    job_url: str
    source: str
    date_posted: Optional[date] = None
    date_scraped: date
    job_type: Optional[str] = None
    is_remote: Optional[bool] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    description_snippet: Optional[str] = None
    skills: Optional[str] = None
    experience_level: Optional[str] = None
    company_url: Optional[str] = None

    def to_row(self) -> list[str]:
        return [
            self.title,
            self.company,
            self.location,
            self.job_url,
            self.source,
            str(self.date_posted) if self.date_posted else "",
            str(self.date_scraped),
            self.job_type or "",
            str(self.is_remote) if self.is_remote is not None else "",
            str(self.salary_min) if self.salary_min else "",
            str(self.salary_max) if self.salary_max else "",
            self.salary_currency or "",
            self.description_snippet or "",
            self.skills or "",
            self.experience_level or "",
            self.company_url or "",
        ]

    @staticmethod
    def sheet_headers() -> list[str]:
        return [
            "Title",
            "Company",
            "Location",
            "Job URL",
            "Source",
            "Date Posted",
            "Date Scraped",
            "Job Type",
            "Is Remote",
            "Salary Min",
            "Salary Max",
            "Salary Currency",
            "Description",
            "Skills",
            "Experience Level",
            "Company URL",
        ]
