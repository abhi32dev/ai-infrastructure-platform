#!/usr/bin/env python3
import os
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from backend.harvesters.greenhouse import fetch_greenhouse_jobs
from backend.harvesters.lever import fetch_lever_jobs
from backend.harvesters.ashby import fetch_ashby_jobs
from backend.database import save_jobs, query_jobs

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "target_companies.json")
VAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "resume_vault", "profile_vault.json")

def harvest_target_companies(selected_names=None):
    if not os.path.exists(CONFIG_PATH):
        return 0, "Config file missing"
        
    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)
        
    companies = cfg.get("companies", [])
    if selected_names:
        companies = [c for c in companies if c.get("name") in selected_names]

    total_harvested = []
    print(f"[*] Aggregating across {len(companies)} selected tech companies...")
    
    for c in companies:
        name = c.get("name")
        ats = c.get("ats", "").lower()
        token = c.get("token")
        
        print(f"[+] Harvesting {name} via {ats.upper()}...")
        if ats == "greenhouse":
            jobs = fetch_greenhouse_jobs(token, name)
        elif ats == "lever":
            jobs = fetch_lever_jobs(token, name)
        elif ats == "ashby":
            jobs = fetch_ashby_jobs(token, name)
        else:
            jobs = []
            
        total_harvested.extend(jobs)
        
    saved = save_jobs(total_harvested)
    return saved, f"Harvested {saved} openings across {len(companies)} companies!"

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
            saved, msg = harvest_target_companies(selected_names=selected)
            self._send_json({"status": "success", "message": msg, "count": saved})
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
                # Deduplicate by name
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
    print(f"🚀 Openings Aggregator Server active on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
