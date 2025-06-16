import sqlite3
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

DB = "companies.db"
app = FastAPI(title="Pre-scraped showcase")


class SearchParams(BaseModel):
    commodity: str
    company_size: str
    geo: str  # Changed from 'geo' to 'geo'
    top_k: int = 20


class Company(BaseModel):
    name: str
    domain: str
    description: str | None = None
    geo: str | None = None
    linkedin: str | None = None


@app.post("/search_supplier_db", response_model=List[Company])
def search_supplier_db(p: SearchParams):
    like_comm = f"%{p.commodity.lower()}%"
    like_loc = f"%{p.geo.lower()}%"

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT name, domain, description, geo as geo, linkedin
        FROM companies
        WHERE instr(lower(commodities), ?) > 0
          AND lower(size) = ?
          AND instr(lower(geo), ?) > 0
        LIMIT ?
        """,
        (like_comm, p.company_size.lower(), like_loc, p.top_k),
    ).fetchall()
    conn.close()

    return [Company(**dict(r)) for r in rows]


@app.get("/health")
def health():
    return {"status": "ok"}
