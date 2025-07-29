# src/filter_jobs.py
"""
Drop jobs that don't match your baseline criteria.

Current rules (tweak any time):
  • Title must contain both 'data' and 'engineer'
  • Location must include the word 'remote'
  • Company can't be in the BLOCKLIST
"""

import re
from typing import Iterable, List, Dict

TITLE_RE = re.compile(r"data.*engineer|engineer.*data", re.I)
REMOTE_USA_PAT = re.compile(
    r"""
    (remote|anywhere|worldwide)         # obvious remote
    |(united\s*states|u\.s\.a?|usa)     # USA‑only jobs
    """,
    re.I | re.X,
)
# ── San Diego onsite / hybrid
SAN_DIEGO_PAT   = re.compile(r"san\s*diego", re.I)
ONSITE_HYBRID_PAT = re.compile(r"onsite|on[-\s]?site|hybrid", re.I)


# Block any companies you never want to see
BLOCKLIST = {"Amazon", "Meta"}   # edit to taste


def _title_ok(title: str) -> bool:
    return bool(TITLE_RE.search(title))

def _location_ok(loc: str) -> bool:
    """Return True if the location meets our keep criteria."""
    loc = loc.strip().lower()

    # 1) Any remote / USA‑wide keyword is an automatic yes
    if REMOTE_USA_PAT.search(loc):
        return True

    # 2) Otherwise, keep only San Diego roles
    if SAN_DIEGO_PAT.search(loc):
        # If they specify onsite or hybrid, that's fine
        if ONSITE_HYBRID_PAT.search(loc) or "onsite" in loc or "hybrid" in loc:
            return True
        # Some posts just say "San Diego, CA" with no mode—accept those too
        return True

    # Everything else is out
    return False


def filter_jobs(jobs: Iterable[Dict]) -> List[Dict]:
    winners: List[Dict] = []
    for j in jobs:
        if not _title_ok(j["title"]):
            continue
        if not _location_ok(j["location"]):
            continue
        if j["company"] in BLOCKLIST:
            continue
        winners.append(j)
    return winners

