# src/enrich_layoffs.py
"""
Adds layoffs_12mo: 1 if company had layoffs in past year, else 0.
Data source: layoffs-tracker CSV on GitHub.
"""

from io import StringIO
from datetime import datetime, timedelta
import httpx, pandas as pd, pathlib, time

CSV_URL = (
    "https://raw.githubusercontent.com/layoffs-tracker/layoffs-tracker/main/data/layoffs.csv"
)
CACHE = pathlib.Path(".cache_layoffs.parquet")

def _load_df() -> pd.DataFrame:
    """Download CSV once per day, cache to Parquet. Robust to header changes."""
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < 86_400:
        return pd.read_parquet(CACHE)

    csv_text = httpx.get(CSV_URL, timeout=30).text
    df = pd.read_csv(StringIO(csv_text))
    # --- normalise column names ---
    df.columns = [c.lower().strip() for c in df.columns]

    # --- find usable date col ---
    date_col = next(
        (c for c in df.columns if "date" in c or "reported" in c or "announced" in c),
        None,
    )
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.rename(columns={date_col: "date"})
    else:
        df["date"] = pd.Timestamp("1900-01-01")   # ASCII dash, not fancy


    # --- find usable company col ---
    comp_col = next((c for c in df.columns if "company" in c), None)
    if comp_col:
        df = df.rename(columns={comp_col: "company"})
    else:
        df["company"] = ""

    df.to_parquet(CACHE, index=False)
    return df


_DF = _load_df()

def layoffs_last_year(company: str) -> int:
    since = datetime.utcnow() - timedelta(days=365)
    hits = _DF[
        (_DF["company"].str.lower() == company.lower()) & (_DF["date"] >= since)
    ]
    return int(not hits.empty)

def enrich(job: dict) -> dict:
    """Return a copy of job with layoffs_12mo flag."""
    j = job.copy()
    j["layoffs_12mo"] = layoffs_last_year(j["company"])
    return j

if __name__ == "__main__":
    print(enrich({"company": "Google"}))

