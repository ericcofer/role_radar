# src/fetch_jobs.py
"""Fetch job posts from Remotive and return a list of dicts."""

import httpx
from urllib.parse import quote_plus

SEARCH_TERM = "data engineer"
API = "https://remotive.com/api/remote-jobs?search="

def fetch_jobs() -> list[dict]:
    url = API + quote_plus(SEARCH_TERM)
    r = httpx.get(url, timeout=20)
    r.raise_for_status()
    return r.json().get("jobs", [])

if __name__ == "__main__":
    jobs = fetch_jobs()
    print(f"Fetched {len(jobs)} jobs")
    for j in jobs[:3]:
        print("•", j["title"], "—", j["company_name"])

