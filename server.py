from flask import Flask, jsonify, request, Response, send_from_directory
from modules.database import init_db, mark_applied
import sqlite3
import json
import subprocess
import sys
import os
import copy
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

app = Flask(__name__, static_folder='dashboard')
DB_PATH = Path(__file__).parent / "jobs.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return send_from_directory('dashboard', 'index.html')

@app.route('/api/jobs')
def get_jobs():
    init_db()
    conn = get_db()
    jobs = conn.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify({
        "jobs": [dict(j) for j in jobs],
        "last_run": "Check terminal for last run time"
    })

@app.route('/api/jobs/<int:job_id>/applied', methods=['POST'])
def set_applied(job_id):
    conn = get_db()
    conn.execute("UPDATE jobs SET status='applied' WHERE id=?", (job_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route('/api/jobs/<int:job_id>/responded', methods=['POST'])
def set_responded(job_id):
    conn = get_db()
    conn.execute("UPDATE jobs SET status='responded' WHERE id=?", (job_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route('/api/run', methods=['POST'])
def run_agent():
    def generate():
        yield f"data: {json.dumps({'log': 'Agent starting...', 'type': 'info', 'progress': 5, 'step': 1})}\n\n"

        env = copy.copy(os.environ)
        env['PYTHONIOENCODING'] = 'utf-8'

        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env
        )
        progress = 10
        step = 1
        for line in process.stdout:
            line = line.strip()
            if not line: continue
            if 'Searching' in line: step = 1; progress = min(progress+5, 30)
            elif 'filtering' in line: step = 2; progress = 35
            elif 'Tailoring' in line: step = 3; progress = min(progress+2, 85)
            elif 'email' in line.lower(): step = 4; progress = min(progress+1, 95)
            elif 'Done' in line: step = 5; progress = 100
            yield f"data: {json.dumps({'log': line, 'progress': progress, 'step': step})}\n\n"
        process.wait()
        yield f"data: {json.dumps({'done': True})}\n\n"
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("Dashboard running at http://localhost:5000")
    app.run(debug=False, port=5000)