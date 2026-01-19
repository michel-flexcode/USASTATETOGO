import sqlite3

conn = sqlite3.connect("data/usa.db")
c = conn.cursor()

# Create junction table
c.execute("""
CREATE TABLE IF NOT EXISTS state_filters (
    state_code TEXT NOT NULL,
    filter_id INTEGER NOT NULL,
    PRIMARY KEY (state_code, filter_id),
    FOREIGN KEY (filter_id) REFERENCES filters(id)
)
""")

# Helper to get filter_id from name
def get_filter_id(name):
    c.execute("SELECT id FROM filters WHERE name = ?", (name,))
    row = c.fetchone()
    if not row:
        raise ValueError(f"Unknown filter: {name}")
    return row[0]

# -------------------
# STATE → FILTER MAP
# -------------------
state_filters = {
    "CA": [
        "assault_weapon_ban",
        "background_checks",
        "permit_required",
        "abortion_allowed",
        "high_income_tax",
        "rent_control",
        "pro_tenant_law",
    ],
    "TX": [
        "open_carry",
        "concealed_carry",
        "no_income_tax",
        "abortion_banned",
        "anti_squat_law",
    ],
    "FL": [
        "concealed_carry",
        "no_income_tax",
        "abortion_restricted",
        "anti_squat_law",
    ],
    "NY": [
        "assault_weapon_ban",
        "background_checks",
        "permit_required",
        "abortion_allowed",
        "high_income_tax",
        "rent_control",
    ],
    "WA": [
        "assault_weapon_ban",
        "background_checks",
        "abortion_allowed",
        "capital_gains_tax",
        "rent_control",
    ],
    "AZ": [
        "open_carry",
        "concealed_carry",
        "no_income_tax",
        "abortion_restricted",
    ],
    "UT": [
        "open_carry",
        "concealed_carry",
        "no_income_tax",
        "abortion_restricted",
        "anti_squat_law",
    ],
}

# -------------------
# INSERT DATA
# -------------------
rows = []

for state, filters in state_filters.items():
    for f in filters:
        rows.append((state, get_filter_id(f)))

c.executemany("""
INSERT OR IGNORE INTO state_filters (state_code, filter_id)
VALUES (?, ?)
""", rows)

conn.commit()
conn.close()

print("✅ State filters seeded successfully")
