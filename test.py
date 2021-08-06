import datetime
import sqlite3

conn = sqlite3.connect('data.db')
cur = conn.cursor()
cur.execute(f'SELECT * FROM films WHERE id in ({", ".join(["1", "2"])})')
print(cur.fetchall())