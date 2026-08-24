import sqlite3
import os
import html
import re
import datetime

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
    
    # 1. Main Jobs Table
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

    # 2. Main Application Tracker Summary Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applied_tracker (
            id TEXT PRIMARY KEY,
            company TEXT,
            title TEXT,
            location TEXT,
            apply_url TEXT,
            applied_date TEXT,
            apply_count INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Applied',
            email_updates TEXT,
            notes TEXT,
            last_applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Persistent Append Log Table for Multiple Applications & Audit Trail
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS application_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT,
            company TEXT,
            title TEXT,
            apply_url TEXT,
            action_type TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    ''')

    # Migration checks
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN salary_min INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN salary_max INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE applied_tracker ADD COLUMN apply_count INTEGER DEFAULT 1")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE applied_tracker ADD COLUMN last_applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
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
    """
    Records an application or appends a repeat log entry if already applied!
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    company = app_data.get("company", "Unknown")
    title = app_data.get("title", "Unknown")
    apply_url = app_data.get("apply_url", "")
    app_id = app_data.get("id") or f"app_{company}_{title}".lower().replace(" ", "_")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT apply_count FROM applied_tracker WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    
    if row:
        new_count = (row[0] or 1) + 1
        cursor.execute('''
            UPDATE applied_tracker 
            SET apply_count = ?, last_applied_at = ?, notes = ?
            WHERE id = ?
        ''', (new_count, now_str, f"Re-applied (Total: {new_count} times)", app_id))
        action_str = f"Re-applied (Attempt #{new_count})"
    else:
        new_count = 1
        cursor.execute('''
            INSERT INTO applied_tracker (id, company, title, location, apply_url, applied_date, apply_count, status, email_updates, notes, last_applied_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            app_id, company, title, app_data.get("location", "US"),
            apply_url, app_data.get("applied_date", now_str[:10]), 1,
            app_data.get("status", "Applied"), "Confirmation Pending",
            "Initial Auto-Apply", now_str
        ))
        action_str = "Initial Application"

    cursor.execute('''
        INSERT INTO application_logs (app_id, company, title, apply_url, action_type, timestamp, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (app_id, company, title, apply_url, action_str, now_str, f"Recorded via UI (Count: {new_count})"))

    conn.commit()
    conn.close()
    return app_id, new_count

def update_application_status(app_id, new_status):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("UPDATE applied_tracker SET status = ? WHERE id = ?", (new_status, app_id))
    
    cursor.execute("SELECT company, title, apply_url FROM applied_tracker WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    if row:
        comp, tit, url = row
        cursor.execute('''
            INSERT INTO application_logs (app_id, company, title, apply_url, action_type, timestamp, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (app_id, comp, tit, url, f"Status set to {new_status}", now_str, f"Updated status to {new_status}"))

    conn.commit()
    conn.close()

def get_applied_tracker():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM applied_tracker ORDER BY last_applied_at DESC")
    apps = [dict(r) for r in cursor.fetchall()]

    for a in apps:
        cursor.execute("SELECT action_type, timestamp, notes FROM application_logs WHERE app_id = ? ORDER BY log_id ASC", (a["id"],))
        a["audit_logs"] = [dict(log) for log in cursor.fetchall()]

    conn.close()
    return apps

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
