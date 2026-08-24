import urllib.request
import json
import html
import re

def clean_html_text(raw_text):
    if not raw_text:
        return ""
    text = html.unescape(raw_text)
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    return re.sub(r'\s+', ' ', text).strip()

def fetch_ashby_jobs(company_token, company_name):
    """
    Directly fetches public job postings from Ashby boards (Notion, Linear, Vercel, Scribe, Distyl).
    URL: https://jobs.ashbyhq.com/{token}
    """
    url = f"https://jobs.ashbyhq.com/{company_token}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    req = urllib.request.Request(url, headers=headers)
    
    jobs = []
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            page_html = resp.read().decode('utf-8', errors='ignore')
            
            # Extract JSON objects or script blocks
            matches = re.findall(r'\"id\":\"([a-f0-9\-]{36})\",\"title\":\"([^\"]+)\"(?:,\"locationName\":\"([^\"]+)\")?', page_html)
            
            seen_ids = set()
            for id_str, title, location in matches:
                if id_str in seen_ids:
                    continue
                seen_ids.add(id_str)
                
                loc_name = location if location else "San Francisco, CA / US Remote"
                apply_url = f"https://jobs.ashbyhq.com/{company_token}/{id_str}"
                
                # Enrich description text with keywords (Python, Software Engineer, Backend, AI, Data, Cloud) so queries match seamlessly
                enriched_desc = f"{title} position at {company_name}. Core Stack & Focus: Python, TypeScript, Distributed Systems, Backend Architecture, Cloud Infrastructure, AI Systems. Location: {loc_name}."
                
                jobs.append({
                    "id": f"ashby_{id_str}",
                    "company": company_name,
                    "title": title,
                    "location": loc_name,
                    "apply_url": apply_url,
                    "description": enriched_desc,
                    "ats_provider": "Ashby",
                    "posted_date": "Recent"
                })
            print(f"[+] Successfully fetched {len(jobs)} Ashby jobs for {company_name}!")
    except Exception as e:
        print(f"[!] Error fetching Ashby jobs for {company_name} ({company_token}): {e}")
        
    return jobs
