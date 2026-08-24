#!/usr/bin/env python3
"""
Openings Aggregator — Live Real-Time Backend API Engine
"""

import os
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import HTTPServer, SimpleHTTPRequestHandler
from backend.harvesters.greenhouse import fetch_greenhouse_jobs
from backend.harvesters.lever import fetch_lever_jobs
from backend.harvesters.ashby import fetch_ashby_jobs
from backend.database import save_jobs, query_jobs, parse_salary_bounds

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "target_companies.json")
VAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "resume_vault", "profile_vault.json")

def harvest_single_company(company):
    name = company.get("name")
    ats = company.get("ats", "").lower()
    token = company.get("token")
    
    print(f"[LIVE BACKEND] Triggering {ats.upper()} API fetch for {name} ({token})...")
    if ats == "greenhouse":
        return fetch_greenhouse_jobs(token, name)
    elif ats == "lever":
        return fetch_lever_jobs(token, name)
    elif ats == "ashby":
        return fetch_ashby_jobs(token, name)
    return []

def live_api_harvest(selected_names=None, query="", location="", min_salary=0):
    if not os.path.exists(CONFIG_PATH):
        return [], "Config file missing"
        
    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)
        
    companies = cfg.get("companies", [])
    if selected_names and len(selected_names) > 0:
        companies = [c for c in companies if c.get("name") in selected_names]

    print(f"[LIVE BACKEND] Launching parallel API harvesters across {len(companies)} companies...")

    all_jobs = []
    # Use multi-threading for fast sub-second parallel API fetches
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(harvest_single_company, c): c for c in companies}
        for future in as_completed(futures):
            try:
                res = future.result()
                all_jobs.extend(res)
            except Exception as e:
                print(f"[!] Worker exception: {e}")

    # Save all fresh live jobs into local SQLite storage
    save_jobs(all_jobs)

    # Filter live payload by search query, location, and min salary on the fly
    filtered = []
    tokens = [t.strip().lower() for t in query.replace(",", " ").split() if t.strip()]
    loc_lower = location.lower().strip()

    for j in all_jobs:
        text_full = f"{j.get('title','')} {j.get('description','')} {j.get('company','')}".lower()
        
        # Check query tokens
        if tokens:
            if not all(t in text_full for t in tokens):
                continue

        # Check location
        if loc_lower:
            if loc_lower not in j.get("location", "").lower() and loc_lower not in text_full:
                continue

        # Check salary floor
        if min_salary > 0:
            s_min, s_max = parse_salary_bounds(text_full)
            if s_max > 0 and s_max < min_salary:
                continue

        filtered.append(j)

    return filtered, f"Live fetched {len(all_jobs)} openings across {len(companies)} native company APIs!"

class AggregatorHTTPHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith("/api/"):
            return path
        root = os.path.join(os.path.dirname(__file__), "..", "frontend")
        req_path = path.split("?")[0]
        if req_path == "/" or req_path == "":
            req_path = "/index.html"
        return os.path.join(root, req_path.lstrip("/"))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/api/jobs":
            query = params.get("q", [""])[0]
            loc = params.get("loc", [""])[0]
            ats = params.get("ats", [""])[0]
            company = params.get("companies", [""])[0]
            min_sal = int(params.get("min_salary", [0])[0])
            sort_by = params.get("sort_by", ["date"])[0]
            limit = int(params.get("limit", [300])[0])
            
            jobs = query_jobs(
                search_query=query,
                location_query=loc,
                ats_filter=ats,
                company_filter=company,
                min_salary=min_sal,
                sort_by=sort_by,
                limit=limit
            )
            
            self._send_json({"status": "success", "count": len(jobs), "jobs": jobs})
            return

        if parsed.path == "/api/companies":
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r") as f:
                    cfg = json.load(f)
            else:
                cfg = {"companies": []}
            self._send_json({"status": "success", "companies": cfg.get("companies", [])})
            return

        if parsed.path == "/api/profile":
            if os.path.exists(VAULT_PATH):
                with open(VAULT_PATH, "r") as f:
                    profile = json.load(f)
            else:
                profile = {}
            self._send_json({"status": "success", "profile": profile})
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            req_json = json.loads(post_data)
        except Exception:
            req_json = {}

        if parsed.path == "/api/harvest":
            selected = req_json.get("companies", None)
            query = req_json.get("query", "")
            location = req_json.get("location", "")
            min_sal = int(req_json.get("min_salary", 0))

            print(f"[REALTIME BACKEND] Triggering live API harvest for query='{query}', location='{location}'...")
            live_jobs, msg = live_api_harvest(
                selected_names=selected,
                query=query,
                location=location,
                min_salary=min_sal
            )

            self._send_json({
                "status": "success",
                "message": msg,
                "count": len(live_jobs),
                "jobs": live_jobs
            })
            return

        if parsed.path == "/api/companies":
            action = req_json.get("action", "add")
            name = req_json.get("name")
            ats = req_json.get("ats")
            token = req_json.get("token")
            category = req_json.get("category", "General Tech")

            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r") as f:
                    cfg = json.load(f)
            else:
                cfg = {"companies": []}

            if action == "add" and name and ats and token:
                cfg["companies"] = [c for c in cfg["companies"] if c.get("name").lower() != name.lower()]
                cfg["companies"].append({"name": name, "ats": ats.lower(), "token": token, "category": category})
                with open(CONFIG_PATH, "w") as f:
                    json.dump(cfg, f, indent=2)
                msg = f"Added {name} ({ats.upper()}) to target list!"
            else:
                msg = "Invalid parameters"

            self._send_json({"status": "success", "message": msg, "companies": cfg.get("companies", [])})
            return

    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, AggregatorHTTPHandler)
    print(f"🚀 Openings Aggregator Real-Time Backend active on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
