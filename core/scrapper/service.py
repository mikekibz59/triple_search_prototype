import logging
from typing import List
from .domain import CompanyDetail, ScrapePostParams
from .factory import get_extractor
from .exceptions import ScrapperServiceException


class ScrapperService:
    """Thin orchestrator: parse → provider → return list (handles top-level errors)."""

    def __init__(self, extractor_name: str):
        if not extractor_name:
            raise ScrapperServiceException("extractor_name must not be empty")

        self._extractor = get_extractor(extractor_name.strip().lower())()

    async def run(self, query: ScrapePostParams) -> List[CompanyDetail]:
        try:
            return await self._extractor.crawl_company_information(query)
        except Exception as e:
            logging.error("ScrapperService error: %s", e)
            raise e
