import urllib.request
import json
import html
import re

def clean_html_text(raw_text):
    if not raw_text:
        return ""
    # 1. Unescape HTML entities like &lt; &gt; &quot; &nbsp; &amp;
    text = html.unescape(raw_text)
    # 2. Remove script and style tags
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # 3. Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # 4. Replace non-breaking spaces and collapse extra whitespace
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    return re.sub(r'\s+', ' ', text).strip()

def fetch_greenhouse_jobs(company_token, company_name):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_token}/jobs?content=true"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    req = urllib.request.Request(url, headers=headers)
    
    jobs = []
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            raw_jobs = data.get("jobs", [])
            
            for j in raw_jobs:
                job_id = f"gh_{j.get('id')}"
                title = j.get("title", "Unknown Title")
                apply_url = j.get("absolute_url", "")
                location = (j.get("location", {}) or {}).get("name", "Remote / Unspecified")
                
                content = j.get("content", "")
                clean_desc = clean_html_text(content)
                
                updated_at = j.get("updated_at", "")
                
                jobs.append({
                    "id": job_id,
                    "company": company_name,
                    "title": title,
                    "location": location,
                    "apply_url": apply_url,
                    "description": clean_desc if len(clean_desc) > 30 else f"{title} at {company_name}",
                    "ats_provider": "Greenhouse",
                    "posted_date": updated_at[:10] if updated_at else "Recent"
                })
    except Exception as e:
        print(f"[!] Error fetching Greenhouse jobs for {company_name} ({company_token}): {e}")
        
    return jobs
