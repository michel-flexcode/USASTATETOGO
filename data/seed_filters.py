import sqlite3

conn = sqlite3.connect("data/usa.db")
c = conn.cursor()

# Create table if not exists
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

# -------------------
# GLOBAL FILTERS
# -------------------
global_filters = [
    ("guns", "guns_global", "Gun laws", "neutral", None),
    ("abortion", "abortion_global", "Abortion laws", "neutral", None),
    ("taxes", "taxes_global", "Taxes", "neutral", None),
    ("housing", "housing_global", "Housing laws", "neutral", None),
]

c.executemany("""
INSERT OR IGNORE INTO filters (category, name, label, side, parent_id)
VALUES (?, ?, ?, ?, ?)
""", global_filters)

# Helper to get parent id
def get_filter_id(name):
    c.execute("SELECT id FROM filters WHERE name = ?", (name,))
    return c.fetchone()[0]

# -------------------
# GUN SUB-FILTERS
# -------------------
guns_parent = get_filter_id("guns_global")

gun_filters = [
    ("guns", "open_carry", "Open carry allowed", "right", guns_parent),
    ("guns", "concealed_carry", "Concealed carry", "right", guns_parent),
    ("guns", "permit_required", "Permit required", "left", guns_parent),
    ("guns", "background_checks", "Background checks", "left", guns_parent),
    ("guns", "assault_weapon_ban", "Assault weapon ban", "left", guns_parent),
]

# -------------------
# ABORTION SUB-FILTERS
# -------------------
abortion_parent = get_filter_id("abortion_global")

abortion_filters = [
    ("abortion", "abortion_allowed", "Abortion allowed", "left", abortion_parent),
    ("abortion", "abortion_restricted", "Abortion restricted", "right", abortion_parent),
    ("abortion", "abortion_banned", "Abortion banned", "right", abortion_parent),
]

# -------------------
# TAX SUB-FILTERS
# -------------------
taxes_parent = get_filter_id("taxes_global")

tax_filters = [
    ("taxes", "no_income_tax", "No income tax", "right", taxes_parent),
    ("taxes", "high_income_tax", "High income tax", "left", taxes_parent),
    ("taxes", "capital_gains_tax", "Capital gains tax", "left", taxes_parent),
]

# -------------------
# HOUSING / SQUAT SUB-FILTERS
# -------------------
housing_parent = get_filter_id("housing_global")

housing_filters = [
    ("housing", "anti_squat_law", "Anti-squat law", "right", housing_parent),
    ("housing", "pro_tenant_law", "Pro-tenant law", "left", housing_parent),
    ("housing", "rent_control", "Rent control", "left", housing_parent),
]

# Insert all sub-filters
all_sub_filters = (
    gun_filters +
    abortion_filters +
    tax_filters +
    housing_filters
)

c.executemany("""
INSERT OR IGNORE INTO filters (category, name, label, side, parent_id)
VALUES (?, ?, ?, ?, ?)
""", all_sub_filters)

conn.commit()
conn.close()

print("✅ Filters seeded successfully")
