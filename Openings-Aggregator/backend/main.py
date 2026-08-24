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

def harvest_all_target_companies():
    if not os.path.exists(CONFIG_PATH):
        return 0, "Config file missing"
        
    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)
        
    companies = cfg.get("companies", [])
    total_harvested = []
    
    print(f"[*] Starting aggregation across {len(companies)} target tech companies...")
    
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
    return saved, f"Successfully harvested {saved} openings across {len(companies)} companies!"

class AggregatorHTTPHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve frontend directory for HTML/JS
        if path.startswith("/api/"):
            return path
        root = os.path.join(os.path.dirname(__file__), "..", "frontend")
        req_path = path.split("?")[0]
        if req_path == "/" or req_path == "":
            req_path = "/index.html"
        return os.path.join(root, req_path.lstrip("/"))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/jobs":
            params = urllib.parse.parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            loc = params.get("loc", [""])[0]
            ats = params.get("ats", [""])[0]
            limit = int(params.get("limit", [100])[0])
            
            jobs = query_jobs(search_query=query, location_query=loc, ats_filter=ats, limit=limit)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "count": len(jobs), "jobs": jobs}).encode("utf-8"))
            return

        if parsed.path == "/api/harvest":
            saved, msg = harvest_all_target_companies()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": msg, "count": saved}).encode("utf-8"))
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        if parsed.path == "/api/harvest":
            saved, msg = harvest_all_target_companies()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": msg, "count": saved}).encode("utf-8"))
            return

        if parsed.path == "/api/config":
            try:
                data = json.loads(post_data)
                with open(CONFIG_PATH, "w") as f:
                    json.dump(data, f, indent=2)
                res = {"status": "success", "message": "Updated target company list!"}
            except Exception as e:
                res = {"status": "error", "message": str(e)}
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, AggregatorHTTPHandler)
    print(f"🚀 Openings Aggregator Live Server running at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
