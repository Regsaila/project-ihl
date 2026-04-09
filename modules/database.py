import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "jobs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            url TEXT UNIQUE,
            description TEXT,
            date TEXT,
            status TEXT DEFAULT 'found',
            applied_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_job(job: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO jobs (title, company, location, url, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (job["title"], job["company"], job["location"], job["url"], job["description"], job["date"]))
        conn.commit()
        return cursor.rowcount > 0  # Returns True if new job, False if duplicate
    finally:
        conn.close()

def mark_applied(url: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE jobs SET status='applied', applied_at=datetime('now')
        WHERE url=?
    """, (url,))
    conn.commit()
    conn.close()

def get_pending_jobs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE status='found'")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized!")