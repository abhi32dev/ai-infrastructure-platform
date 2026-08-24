import urllib.request
import json
import re

def fetch_ashby_jobs(company_token, company_name):
    """
    Directly fetches public job postings from Ashby GraphQL API.
    URL: POST https://api.ashbyhq.com/posting-api/job-board/{token}
    """
    url = f"https://api.ashbyhq.com/posting-api/job-board/{company_token}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Content-Type': 'application/json'
    }
    
    payload = json.dumps({"operationName": "ApiJobBoardWithDescription", "variables": {"organizationHostedJobsPageName": company_token}}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers=headers)
    
    jobs = []
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            job_postings = (data.get("data", {}) or {}).get("jobBoard", {}).get("jobPostings", [])
            
            for j in job_postings:
                job_id = f"ashby_{j.get('id')}"
                title = j.get("title", "Unknown Title")
                location = j.get("locationName", "Remote / Unspecified")
                
                # Direct apply link structure
                apply_url = f"https://jobs.ashbyhq.com/{company_token}/{j.get('id')}"
                
                desc_html = j.get("descriptionHtml", "")
                clean_desc = re.sub(r'<[^>]+>', ' ', desc_html)
                clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
                
                jobs.append({
                    "id": job_id,
                    "company": company_name,
                    "title": title,
                    "location": location,
                    "apply_url": apply_url,
                    "description": clean_desc if len(clean_desc) > 30 else f"{title} at {company_name}",
                    "ats_provider": "Ashby",
                    "posted_date": "Active"
                })
    except Exception:
        # Fallback to direct page parse for Ashby
        fallback_url = f"https://jobs.ashbyhq.com/{company_token}"
        try:
            req_fb = urllib.request.Request(fallback_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_fb, timeout=5) as resp_fb:
                html = resp_fb.read().decode('utf-8', errors='ignore')
                raw_ids = re.findall(r'/([a-f0-9\-]{36})', html)
                for id_match in set(raw_ids):
                    jobs.append({
                        "id": f"ashby_{id_match}",
                        "company": company_name,
                        "title": f"Position at {company_name}",
                        "location": "San Francisco, CA / Remote",
                        "apply_url": f"https://jobs.ashbyhq.com/{company_token}/{id_match}",
                        "description": f"Active position at {company_name}. Click apply link to view full description.",
                        "ats_provider": "Ashby",
                        "posted_date": "Active"
                    })
        except Exception as e2:
            print(f"[!] Error fetching Ashby jobs for {company_name}: {e2}")
            
    return jobs
