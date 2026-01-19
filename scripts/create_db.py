import sqlite3
import os

os.makedirs("data", exist_ok=True)
db_path = os.path.join("data", "usa.db")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# STATES
c.execute("""
CREATE TABLE IF NOT EXISTS states (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
""")

# FILTERS
c.execute("""
CREATE TABLE IF NOT EXISTS filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    name TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    side TEXT CHECK(side IN ('left','right','neutral')),
    parent_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES filters(id)
)
""")

# STATE ↔ FILTER RELATION
c.execute("""
CREATE TABLE IF NOT EXISTS state_filters (
    state_code TEXT NOT NULL,
    filter_id INTEGER NOT NULL,
    PRIMARY KEY (state_code, filter_id),
    FOREIGN KEY (state_code) REFERENCES states(code),
    FOREIGN KEY (filter_id) REFERENCES filters(id)
)
""")

conn.commit()
conn.close()

print("✅ Database structure created")
