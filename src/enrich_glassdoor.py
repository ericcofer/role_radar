# src/enrich_glassdoor.py
"""
Adds glassdoor_rating: float 1–5 (None if lookup fails).
Simple JSON cache so we never hammer the API twice.
"""

import json, httpx, pathlib
from urllib.parse import quote_plus
from typing import Optional, Dict
from slugify import slugify 



CACHE = pathlib.Path(".cache_glassdoor.json")
cache: Dict[str, Optional[float]] = {}

if CACHE.exists():
    cache = json.loads(CACHE.read_text())

API = "https://rugg.ai/api/glassdoor?company="

def _fetch_rating(company: str) -> Optional[float]:
    """
    Try multiple slug variations until one sticks.
    """
    candidates = {
        company,
        company.replace(",", ""),
        company.replace("Inc.", "").replace("Inc", "").strip(),
        slugify(company, separator="-"),      # e.g. "snowflake-inc"
        slugify(company.split()[0]),          # e.g. "snowflake"
    }

    for cand in candidates:
        url = API + quote_plus(cand)
        try:
            r = httpx.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if "rating" in data and data["rating"]:
                    return float(data["rating"])
        except Exception:
            continue

    return None        # all attempts failed

def enrich(job: dict) -> dict:
    j = job.copy()
    name = j["company"]

    if name not in cache:
        cache[name] = _fetch_rating(name)
        CACHE.write_text(json.dumps(cache))

    j["glassdoor_rating"] = cache[name]
    return j

if __name__ == "__main__":
    print(enrich({"company": "Snowflake"}))

