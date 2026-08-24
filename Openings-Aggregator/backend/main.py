#!/usr/bin/env python3
"""
Openings Aggregator — Live Real-Time Backend API Engine (Strict US Location Filter)
"""

import os
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import HTTPServer, SimpleHTTPRequestHandler
from backend.harvesters.greenhouse import fetch_greenhouse_jobs
from backend.harvesters.lever import fetch_lever_jobs
from backend.harvesters.ashby import fetch_ashby_jobs
from backend.database import save_jobs, query_jobs, parse_salary_bounds, get_applied_tracker, record_application, update_application_status

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "target_companies.json")
VAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "resume_vault", "profile_vault.json")

# Keywords indicating NON-US locations
NON_US_KEYWORDS = [
  "berlin", "london", "uk", "united kingdom", "germany", "france", "paris", "canada", "toronto",
  "vancouver", "india", "bangalore", "bengaluru", "singapore", "apac", "emea", "tokyo", "japan",
  "australia", "sydney", "melbourne", "brazil", "amsterdam", "netherlands", "spain", "madrid",
  "barcelona", "dublin", "ireland", "poland", "warsaw", "sweden", "stockholm", "munich", "zurich",
  "switzerland", "mexico", "israel", "tel aviv"
]

# State postal codes & US location indicators
US_LOCATION_INDICATORS = [
  "us", "usa", "united states", "remote - us", "remote, us", "remote (us)", "remote - usa",
  "ca", "ny", "tx", "wa", "ma", "co", "il", "ga", "fl", "nc", "va", "or", "az", "ut", "nj", "pa",
  "san francisco", "palo alto", "mountain view", "redwood city", "fremont", "los angeles", "san jose",
  "new york", "austin", "seattle", "boston", "chicago", "denver", "atlanta", "miami"
]

def is_us_location(location_str, full_text=""):
  loc = (location_str or "").lower().strip()
  text = (full_text or "").lower()

  # 1. Reject if explicitly matches non-US countries/cities
  for non_us in NON_US_KEYWORDS:
    if non_us in loc:
      return False

  # 2. Check if matches US indicators or state codes
  if any(ind in loc for ind in US_LOCATION_INDICATORS):
    return True

  # 3. Default to True if unspecified/remote unless flagged as non-US
  if "remote" in loc or "unspecified" in loc or not loc:
    return not any(non_us in loc for non_us in NON_US_KEYWORDS)

  return True

def harvest_single_company(company):
  name = company.get("name")
  ats = company.get("ats", "").lower()
  token = company.get("token")

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

  all_jobs = []
  with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(harvest_single_company, c): c for c in companies}
    for future in as_completed(futures):
      try:
        res = future.result()
        all_jobs.extend(res)
      except Exception as e:
        print(f"[!] Worker exception: {e}")

  save_jobs(all_jobs)

  filtered = []
  tokens = [
      t.strip().lower() for t in query.replace(",", " ").split() if t.strip()
  ]
  user_loc = location.lower().strip()

  for j in all_jobs:
    loc = j.get("location", "")
    text_full = (
        f"{j.get('title','')} {j.get('description','')} {j.get('company','')}"
        .lower()
    )

    # STRICT US ONLY FILTER: Reject any job outside US
    if not is_us_location(loc, text_full):
      continue

    # If user specifies a location sub-filter (e.g. "California", "San Francisco"), apply it
    if user_loc:
      if user_loc not in loc.lower() and user_loc not in text_full:
        continue

    # Check query tokens
    if tokens:
      if not all(t in text_full for t in tokens):
        continue

    # Check salary floor
    if min_salary > 0:
      s_min, s_max = parse_salary_bounds(text_full)
      if s_max > 0 and s_max < min_salary:
        continue

    filtered.append(j)

  return (
      filtered,
      f"Live fetched {len(filtered)} US openings across {len(companies)} company"
      " APIs!",
  )


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
          limit=limit,
      )

      # Filter SQLite results for US-only as well
      us_jobs = [j for j in jobs if is_us_location(j.get("location", ""))]
      self._send_json({"status": "success", "count": len(us_jobs), "jobs": us_jobs})
      return

    if parsed.path == "/api/companies":
      if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
          cfg = json.load(f)
      else:
        cfg = {"companies": []}
      self._send_json(
          {"status": "success", "companies": cfg.get("companies", [])}
      )
      return

    if parsed.path == "/api/tracker":
      apps = get_applied_tracker()
      self._send_json({"status": "success", "count": len(apps), "applications": apps})
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
    content_length = int(self.headers.get("Content-Length", 0))
    post_data = (
        self.rfile.read(content_length).decode("utf-8")
        if content_length > 0
        else "{}"
    )

    try:
      req_json = json.loads(post_data)
    except Exception:
      req_json = {}

    if parsed.path == "/api/tracker":
      action = req_json.get("action", "record")
      if action == "update_status":
        update_application_status(req_json.get("id"), req_json.get("status"))
        msg = "Application status updated!"
      else:
        record_application(req_json)
        msg = "Application recorded in local tracker database!"
      self._send_json({"status": "success", "message": msg})
      return

    if parsed.path == "/api/profile":
        raw_text = req_json.get("raw_text", "")
        parsed_data = req_json.get("profile", {})

        if raw_text:
            # Save raw text note alongside json
            raw_path = os.path.join(os.path.dirname(__file__), "..", "resume_vault", "notes.txt")
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw_text)

        if parsed_data:
            with open(VAULT_PATH, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, indent=2)

        self._send_json({"status": "success", "message": "Profile notes & vault updated!"})
        return

    if parsed.path == "/api/harvest":
      selected = req_json.get("companies", None)
      query = req_json.get("query", "")
      location = req_json.get("location", "")
      min_sal = int(req_json.get("min_salary", 0))

      live_jobs, msg = live_api_harvest(
          selected_names=selected,
          query=query,
          location=location,
          min_salary=min_sal,
      )

      self._send_json({
          "status": "success",
          "message": msg,
          "count": len(live_jobs),
          "jobs": live_jobs,
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
        cfg["companies"] = [
            c
            for c in cfg["companies"]
            if c.get("name").lower() != name.lower()
        ]
        cfg["companies"].append({
            "name": name,
            "ats": ats.lower(),
            "token": token,
            "category": category,
        })
        with open(CONFIG_PATH, "w") as f:
          json.dump(cfg, f, indent=2)
        msg = f"Added {name} ({ats.upper()}) to target list!"
      else:
        msg = "Invalid parameters"

      self._send_json(
          {"status": "success", "message": msg, "companies": cfg.get("companies", [])}
      )
      return

  def _send_json(self, data, code=200):
    self.send_response(code)
    self.send_header("Content-Type", "application/json")
    self.send_header("Access-Control-Allow-Origin", "*")
    self.end_headers()
    self.wfile.write(json.dumps(data).encode("utf-8"))


def run_server(port=8000):
  server_address = ("", port)
  httpd = HTTPServer(server_address, AggregatorHTTPHandler)
  print(
      "🚀 Openings Aggregator Server (Strict US Only Filter) active on"
      f" http://localhost:{port}"
  )
  httpd.serve_forever()


if __name__ == "__main__":
  run_server()
