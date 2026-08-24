import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "openings.db")

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_jobs(jobs):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    saved_count = 0
    for j in jobs:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO jobs (id, company, title, location, apply_url, description, ats_provider, posted_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                j["id"], j["company"], j["title"], j["location"],
                j["apply_url"], j["description"], j["ats_provider"], j["posted_date"]
            ))
            saved_count += 1
        except Exception as e:
            print(f"Database error for job {j.get('id')}: {e}")
            
    conn.commit()
    conn.close()
    return saved_count

def query_jobs(search_query="", location_query="", ats_filter="", limit=100):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = "SELECT * FROM jobs WHERE 1=1"
    params = []
    
    if search_query:
        # Split search tokens (e.g. "python, aws" or "backend")
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
        
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
