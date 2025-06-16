import json, pathlib, sqlite3

DB = "companies.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.executescript(
    """
    DROP TABLE IF EXISTS companies;
    CREATE TABLE companies (
        id INTEGER PRIMARY KEY,
        name TEXT,
        domain TEXT,
        description TEXT,
        commodities TEXT,   -- "roofing|building materials"
        size TEXT,
        geo TEXT,
        linkedin TEXT
    );
    """
)

for fp in pathlib.Path("sample_data").glob("*.json"):
    data = json.loads(fp.read_text())
    
    # Handle both single objects and arrays
    if isinstance(data, list):
        companies = data
    else:
        companies = [data]
    
    for doc in companies:
        # Handle commodity field (could be string or list)
        commodity = doc.get("commodity", [])
        if isinstance(commodity, str):
            commodity_str = commodity
        else:
            commodity_str = "|".join(commodity)
        
        cur.execute(
            """
            INSERT INTO companies
            (name, domain, description, commodities, size, geo, linkedin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc["name"],
                doc["domain"],
                doc.get("description", ""),
                commodity_str,
                doc.get("size", ""),
                doc.get("geo", ""),
                doc.get("linkedIn", ""),
            ),
        )

conn.commit()
conn.close()
print("✓ SQLite DB built:", DB)