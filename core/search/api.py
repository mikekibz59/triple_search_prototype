from fastapi import FastAPI, HTTPException
from .domain import SearchQuery, SearchResult
from .service import SearchService
from .exceptions import GoogleSearchException, GoogleQuotaExceeded, GoogleAuthError

app = FastAPI(title="Search Service")

# initialise once; provider is picked via env-var SEARCH_PROVIDER (optional)
service = SearchService()


@app.post("/search", response_model=list[SearchResult])
async def search_endpoint(q: SearchQuery):
    try:
        return service.run(q)
    except GoogleQuotaExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))
    except GoogleAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except GoogleSearchException as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
