import urllib.request
import json
import re
import datetime

def extract_employment_type(commitment_str, title, text=""):
    full = f"{commitment_str} {title} {text}".lower()
    if "contract" in full or "freelance" in full:
        return "Contract"
    elif "intern" in full or "co-op" in full or "coop" in full:
        return "Internship"
    elif "part-time" in full or "part time" in full:
        return "Part-Time"
    elif "temp" in full or "temporary" in full:
        return "Temporary"
    return "Full-Time"

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

def fetch_lever_jobs(company_token, company_name):
    url = f"https://api.lever.co/v0/postings/{company_token}?mode=json"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    req = urllib.request.Request(url, headers=headers)
    
    jobs = []
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            for j in data:
                raw_id = j.get('id')
                job_id = f"lever_{raw_id}"
                title = j.get("text", "Unknown Title")
                
                apply_url = j.get("applyUrl", "") or f"https://jobs.lever.co/{company_token}/{raw_id}/apply"
                
                cats = j.get("categories", {}) or {}
                location = cats.get("location", "Remote / Unspecified")
                commitment = cats.get("commitment", "")
                team = cats.get("team", "")
                
                description_plain = j.get("descriptionPlain", "") or j.get("description", "")
                clean_desc = re.sub(r'<[^>]+>', ' ', description_plain)
                clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
                
                emp_type = extract_employment_type(commitment, title, clean_desc)
                salary_str, s_min, s_max = extract_salary_range(clean_desc, title)

                jobs.append({
                    "id": job_id,
                    "company": company_name,
                    "title": title,
                    "location": f"{location} ({commitment})" if commitment else location,
                    "employment_type": emp_type,
                    "apply_url": apply_url,
                    "description": clean_desc if len(clean_desc) > 30 else f"{title} at {company_name} - {team}",
                    "ats_provider": "Lever",
                    "posted_date": today_date,
                    "salary_min": s_min,
                    "salary_max": s_max,
                    "salary_display": salary_str
                })
    except Exception as e:
        print(f"[!] Error fetching Lever jobs for {company_name} ({company_token}): {e}")
        
    return jobs
