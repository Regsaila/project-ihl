import sqlite3

conn = sqlite3.connect('jobs.db')
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables:', cur.fetchall())

cur.execute('SELECT * FROM jobs LIMIT 20')
rows = cur.fetchall()
for r in rows:
    print(r)