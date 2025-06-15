from typing import Optional, List
from pydantic import BaseModel


class SearchQuery(BaseModel):
    commodity: str
    location: str
    company_size: str


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    score: Optional[int] = None
    matched_terms: Optional[List[str]] = None
    source_url: Optional[str] = None
