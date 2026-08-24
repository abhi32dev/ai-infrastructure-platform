import sqlite3
import os
import html
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "openings.db")

def clean_text(raw_text):
    if not raw_text:
        return ""
    text = html.unescape(raw_text)
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    return re.sub(r'\s+', ' ', text).strip()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            company TEXT,
            title TEXT,
            location TEXT,
            apply_url TEXT,
            description TEXT,
            ats_provider TEXT,
            posted_date TEXT,
            salary_min INTEGER DEFAULT 0,
            salary_max INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Application Tracker Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applied_tracker (
            id TEXT PRIMARY KEY,
            company TEXT,
            title TEXT,
            location TEXT,
            apply_url TEXT,
            applied_date TEXT,
            status TEXT DEFAULT 'Applied',
            email_updates TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN salary_min INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN salary_max INTEGER DEFAULT 0")
    except Exception:
        pass

    conn.commit()
    conn.close()

def parse_salary_bounds(text):
    if not text:
        return 0, 0
    matches = re.findall(r'\$([0-9]{2,3})(?:,([0-9]{3}))?|([0-9]{2,3})k', text.lower())
    vals = []
    for m in matches:
        if m[0]:
            val = int(m[0]) * 1000 + (int(m[1]) if m[1] else 0)
            vals.append(val)
        elif m[2]:
            vals.append(int(m[2]) * 1000)
    if not vals:
        return 0, 0
    return min(vals), max(vals)

def save_jobs(jobs):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    saved_count = 0
    for j in jobs:
        try:
            clean_desc = clean_text(j.get("description", ""))
            s_min, s_max = parse_salary_bounds(f"{j.get('title', '')} {clean_desc} {j.get('location', '')}")
            cursor.execute('''
                INSERT OR REPLACE INTO jobs (id, company, title, location, apply_url, description, ats_provider, posted_date, salary_min, salary_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                j["id"], j["company"], j["title"], j["location"],
                j["apply_url"], clean_desc, j["ats_provider"], j["posted_date"],
                s_min, s_max
            ))
            saved_count += 1
        except Exception as e:
            print(f"Database error for job {j.get('id')}: {e}")
            
    conn.commit()
    conn.close()
    return saved_count

def record_application(app_data):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    app_id = app_data.get("id") or f"app_{app_data.get('company')}_{app_data.get('title')}".lower().replace(" ", "_")
    
    cursor.execute('''
        INSERT OR REPLACE INTO applied_tracker (id, company, title, location, apply_url, applied_date, status, email_updates, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        app_id,
        app_data.get("company", "Unknown"),
        app_data.get("title", "Unknown"),
        app_data.get("location", "US"),
        app_data.get("apply_url", ""),
        app_data.get("applied_date", "2026-08-23"),
        app_data.get("status", "Applied"),
        app_data.get("email_updates", "Confirmation Pending"),
        app_data.get("notes", "Auto-applied via Openings Aggregator")
    ))
    conn.commit()
    conn.close()
    return app_id

def update_application_status(app_id, new_status):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE applied_tracker SET status = ? WHERE id = ?", (new_status, app_id))
    conn.commit()
    conn.close()

def get_applied_tracker():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applied_tracker ORDER BY created_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def query_jobs(search_query="", location_query="", ats_filter="", company_filter="", min_salary=0, sort_by="date", limit=300):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = "SELECT * FROM jobs WHERE 1=1"
    params = []
    
    if search_query:
        tokens = [t.strip() for t in search_query.replace(",", " ").split() if t.strip()]
        for t in tokens:
            sql += " AND (title LIKE ? OR description LIKE ? OR company LIKE ?)"
            params.extend([f"%{t}%", f"%{t}%", f"%{t}%"])
            
    if location_query:
        sql += " AND location LIKE ?"
        params.append(f"%{location_query}%")
        
    if ats_filter:
        sql += " AND ats_provider LIKE ?"
        params.append(f"%{ats_filter}%")

    if company_filter:
        c_list = [c.strip() for c in company_filter.split(",") if c.strip()]
        placeholders = ",".join(["?"] * len(c_list))
        sql += f" AND company IN ({placeholders})"
        params.extend(c_list)

    if min_salary > 0:
        sql += " AND (salary_max >= ? OR salary_max = 0)"
        params.append(min_salary)
        
    if sort_by == "salary_desc":
        sql += " ORDER BY salary_max DESC, created_at DESC"
    elif sort_by == "company":
        sql += " ORDER BY company ASC, created_at DESC"
    elif sort_by == "title":
        sql += " ORDER BY title ASC, created_at DESC"
    else:
        sql += " ORDER BY created_at DESC"
        
    sql += " LIMIT ?"
    params.append(limit)
    
    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
