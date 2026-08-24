#!/usr/bin/env python3
"""
export_dataset.py — CLI Dataset Exporter for Openings Aggregator

Exports harvested database jobs to CSV and Markdown.
"""

import os, csv, json
from backend.database import query_jobs

OUTPUT_DIR = os.path.dirname(__file__)

def export():
    jobs = query_jobs(limit=1000)
    print(f"[*] Exporting {len(jobs)} harvested job records...")

    csv_path = os.path.join(OUTPUT_DIR, "openings_dataset.csv")
    md_path = os.path.join(OUTPUT_DIR, "OPENINGS_DATASET.md")

    headers = ["Company", "Job Title", "Location", "ATS Engine", "Apply URL", "Description"]

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for j in jobs:
            writer.writerow({
                "Company": j.get("company", ""),
                "Job Title": j.get("title", ""),
                "Location": j.get("location", ""),
                "ATS Engine": j.get("ats_provider", ""),
                "Apply URL": j.get("apply_url", ""),
                "Description": j.get("description", "")
            })

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# OPENINGS AGGREGATOR DATASET ({len(jobs)} Records)\n\n")
        f.write("| Company | Job Title | Location | ATS Engine | Direct Apply Link |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for j in jobs:
            f.write(f"| **{j.get('company')}** | {j.get('title')} | {j.get('location')} | `{j.get('ats_provider')}` | [Apply ↗]({j.get('apply_url')}) |\n")

    print(f"[+] Exported CSV: {csv_path}")
    print(f"[+] Exported Markdown: {md_path}")

if __name__ == "__main__":
    export()
