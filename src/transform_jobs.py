# src/transform_jobs.py
"""Take raw Remotive rows ➜ slim job dicts."""

from datetime import datetime

def transform(raw_job: dict) -> dict:
    return {
        "title":    raw_job["title"],
        "company":  raw_job["company_name"],
        "location": raw_job["candidate_required_location"],
        "posted":   datetime.fromisoformat(raw_job["publication_date"]).date().isoformat(),
        "url":      raw_job["url"],
    }

