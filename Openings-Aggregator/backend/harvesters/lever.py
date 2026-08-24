import urllib.request
import json
import re

def fetch_lever_jobs(company_token, company_name):
    """
    Directly fetches public job postings from Lever API.
    URL: https://api.lever.co/v0/postings/{token}?mode=json
    """
    url = f"https://api.lever.co/v0/postings/{company_token}?mode=json"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    req = urllib.request.Request(url, headers=headers)
    
    jobs = []
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            for j in data:
                job_id = f"lever_{j.get('id')}"
                title = j.get("text", "Unknown Title")
                apply_url = j.get("hostedUrl", "")
                
                cats = j.get("categories", {}) or {}
                location = cats.get("location", "Remote / Unspecified")
                commitment = cats.get("commitment", "")
                team = cats.get("team", "")
                
                description_plain = j.get("descriptionPlain", "") or j.get("description", "")
                clean_desc = re.sub(r'<[^>]+>', ' ', description_plain)
                clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
                
                created_at = j.get("createdAt", 0)
                
                jobs.append({
                    "id": job_id,
                    "company": company_name,
                    "title": title,
                    "location": f"{location} ({commitment})" if commitment else location,
                    "apply_url": apply_url,
                    "description": clean_desc if len(clean_desc) > 30 else f"{title} at {company_name} - {team}",
                    "ats_provider": "Lever",
                    "posted_date": "Recent"
                })
    except Exception as e:
        print(f"[!] Error fetching Lever jobs for {company_name} ({company_token}): {e}")
        
    return jobs
