import logging
from typing import List
from .domain import SearchQuery, SearchResult
from .factory import get_provider
from .exceptions import GoogleSearchException, SearchServiceException


class SearchService:
    """Thin orchestrator: parse → provider → return list (handles top-level errors)."""

    def __init__(self, provider_name: str = "google"):
        if not provider_name:
            raise SearchServiceException("provider_name must not be empty")

        self.provider = get_provider(provider_name.strip().lower())()

    def run(self, query: SearchQuery) -> List[SearchResult]:
        try:
            return self.provider.search(query)
        except GoogleSearchException as e:
            # Log once here; API layer will convert to HTTP status
            logging.error("SearchService error: %s", e)
            raise e
