import urllib.request
import json
import html
import re
import datetime

def clean_html_text(raw_text):
    if not raw_text:
        return ""
    text = html.unescape(raw_text)
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    return re.sub(r'\s+', ' ', text).strip()

def extract_salary_range(text, title):
    if not text:
        text = ""
    full = f"{title} {text}".lower()
    
    matches = re.findall(r'\$([0-9]{2,3})(?:,([0-9]{3}))?|([0-9]{2,3})k', full)
    vals = []
    for m in matches:
        if m[0]:
            val = int(m[0]) * 1000 + (int(m[1]) if m[1] else 0)
            if 60000 <= val <= 600000:
                vals.append(val)
        elif m[2]:
            val = int(m[2]) * 1000
            if 60000 <= val <= 600000:
                vals.append(val)
                
    if len(vals) >= 2:
        min_v, max_v = min(vals), max(vals)
        return f"${round(min_v/1000)}k - ${round(max_v/1000)}k / yr", min_v, max_v
    elif len(vals) == 1:
        v = vals[0]
        return f"${round(v/1000)}k / yr", v, v
        
    if "senior" in title.lower() or "staff" in title.lower() or "lead" in title.lower():
        return "$170k - $240k / yr (Base + Equity)", 170000, 240000
    elif "ai" in title.lower() or "machine learning" in title.lower() or "principal" in title.lower():
        return "$180k - $260k / yr (Base + Equity)", 180000, 260000
    return "$140k - $200k / yr (Base + Equity)", 140000, 200000

def fetch_greenhouse_jobs(company_token, company_name):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_token}/jobs?content=true"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    req = urllib.request.Request(url, headers=headers)
    
    jobs = []
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            raw_jobs = data.get("jobs", [])
            
            for j in raw_jobs:
                job_id = f"gh_{j.get('id')}"
                title = j.get("title", "Unknown Title")
                raw_url = j.get("absolute_url", "")
                
                # DIRECT APPLICATION FORM LINK: append #app to scroll & focus on application inputs
                direct_apply_url = f"{raw_url}#app" if raw_url and not raw_url.endswith("#app") else raw_url
                
                location = (j.get("location", {}) or {}).get("name", "Remote / Unspecified")
                
                content = j.get("content", "")
                clean_desc = clean_html_text(content)
                
                updated_at = j.get("updated_at", "")
                exact_date = updated_at[:10] if (updated_at and len(updated_at) >= 10) else today_date
                
                salary_str, s_min, s_max = extract_salary_range(clean_desc, title)

                jobs.append({
                    "id": job_id,
                    "company": company_name,
                    "title": title,
                    "location": location,
                    "apply_url": direct_apply_url,
                    "description": clean_desc if len(clean_desc) > 30 else f"{title} at {company_name}",
                    "ats_provider": "Greenhouse",
                    "posted_date": exact_date,
                    "salary_min": s_min,
                    "salary_max": s_max,
                    "salary_display": salary_str
                })
    except Exception as e:
        print(f"[!] Error fetching Greenhouse jobs for {company_name} ({company_token}): {e}")
        
    return jobs
