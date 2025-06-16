import os
import requests
import typing
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .config import SCRAPE_URL, SEARCH_URL


app = FastAPI(title="On-demand gateway")

class CompanyScrapeInfo(BaseModel):
    title: str
    company_scrape_link: str


class ScrapePostParams(BaseModel):
    extractor: typing.Optional[str] = 'generic'
    scrape_links: typing.List[CompanyScrapeInfo]


class SearchIn(BaseModel):
    commodity: str
    company_size: str
    geo: str


@app.post("/triple-search")
def triple_search(q: SearchIn):
    try:
        # 1. hit Search service
        resp = requests.post(SEARCH_URL, json=q.model_dump(), timeout=None)
        resp.raise_for_status()

        search_results = resp.json() or []
        if not search_results:
            return []

        company_infos = [
            CompanyScrapeInfo(
                title=item["title"],
                company_scrape_link=item["url"],
            )
            for item in search_results
        ]

        scrape_payload = ScrapePostParams(scrape_links=company_infos)

        scraped_resp = requests.post(SCRAPE_URL, json=scrape_payload.model_dump(), timeout=None)
        scrape_payload.raise_for_status()
        return scraped_resp.json()

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
