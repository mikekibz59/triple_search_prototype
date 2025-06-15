from fastapi import FastAPI, HTTPException
from .domain import ScrapePostParams, CompanyDetail
from .service import ScrapperService
from .exceptions import GenericExtractorImproperlyConfiguredException

app = FastAPI(title="Scrapper Service")


@app.post("/scrape", response_model=list[CompanyDetail])
async def search_endpoint(q: ScrapePostParams):
    try:
        if not q.extractor:
            q.extractor = "generic"

        service = ScrapperService(q.extractor)
        return await service.run(q)
    except GenericExtractorImproperlyConfiguredException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
