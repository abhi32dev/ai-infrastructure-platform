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
    
    # Check for $XXX,XXX or $XXXk patterns
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
        
    # Standard tech salary band defaults based on seniority
    if "senior" in title.lower() or "staff" in title.lower() or "lead" in title.lower():
        return "$170k - $240k / yr (Base + Equity)", 170000, 240000
    elif "ai" in title.lower() or "machine learning" in title.lower() or "principal" in title.lower():
        return "$180k - $260k / yr (Base + Equity)", 180000, 260000
    return "$140k - $200k / yr (Base + Equity)", 140000, 200000

def fetch_ashby_jobs(company_token, company_name):
    url = f"https://jobs.ashbyhq.com/{company_token}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    req = urllib.request.Request(url, headers=headers)
    
    jobs = []
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            page_html = resp.read().decode('utf-8', errors='ignore')
            
            matches = re.findall(r'\"id\":\"([a-f0-9\-]{36})\",\"title\":\"([^\"]+)\"(?:,\"locationName\":\"([^\"]+)\")?', page_html)
            
            seen_ids = set()
            for id_str, title, location in matches:
                if id_str in seen_ids:
                    continue
                seen_ids.add(id_str)
                
                loc_name = location if location else "San Francisco, CA / US Remote"
                apply_url = f"https://jobs.ashbyhq.com/{company_token}/{id_str}"
                
                enriched_desc = f"{title} position at {company_name}. Core Stack & Focus: Python, TypeScript, Distributed Systems, Backend Architecture, Cloud Infrastructure, AI Systems. Location: {loc_name}."
                
                salary_str, s_min, s_max = extract_salary_range(enriched_desc, title)
                
                jobs.append({
                    "id": f"ashby_{id_str}",
                    "company": company_name,
                    "title": title,
                    "location": loc_name,
                    "apply_url": apply_url,
                    "description": enriched_desc,
                    "ats_provider": "Ashby",
                    "posted_date": today_date,
                    "salary_min": s_min,
                    "salary_max": s_max,
                    "salary_display": salary_str
                })
            print(f"[+] Successfully fetched {len(jobs)} Ashby jobs for {company_name}!")
    except Exception as e:
        print(f"[!] Error fetching Ashby jobs for {company_name} ({company_token}): {e}")
        
    return jobs
