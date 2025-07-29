#!/usr/bin/env python
"""
run_pipeline.py
---------------
Fetch → transform → filter → print.
Add --save out.json to write the results; otherwise prints to stdout.
"""

import argparse, json, pathlib, sys
from datetime import datetime
from src.enrich_layoffs import enrich as enrich_layoffs
from src.fetch_jobs import fetch_jobs
from src.transform_jobs import transform
from src.filter_jobs import filter_jobs
from src.enrich_glassdoor import enrich as enrich_gd


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Role‑Radar pipeline")
    parser.add_argument("--save", metavar="FILE", help="Save output JSON instead of printing")
    args = parser.parse_args()

    raw = fetch_jobs()
    transformed = [transform(j) for j in raw]
    filtered = filter_jobs(transformed)
    enriched = [enrich_layoffs(j) for j in filtered]
    enriched = [enrich_gd(j) for j in enriched]   # note: chain after layoffs


    print(f"Raw: {len(raw)} | After filter: {len(filtered)}", file=sys.stderr)

    if args.save:
        path = pathlib.Path(args.save)
        path.parent.mkdir(parents=True, exist_ok=True)  # <‑‑ ensures output/ exists
        path.write_text(json.dumps(enriched, indent=2)) # dump the enriched list
        print(f"Wrote {len(enriched)} jobs → {path}", file=sys.stderr)
    else:
        print(json.dumps(enriched, indent=2))


if __name__ == "__main__":
    main()

