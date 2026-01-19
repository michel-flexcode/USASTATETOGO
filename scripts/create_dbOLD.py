import sqlite3
import os

# Create data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# DB path inside data folder
db_path = os.path.join("data", "usa.db")

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state TEXT UNIQUE,
    gun_rights INTEGER,
    tax_free INTEGER,
    anti_squat INTEGER,
    left_law INTEGER,
    abortion INTEGER
)
""")

conn.commit()
conn.close()
