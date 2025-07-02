import secrets
import string
import typing
import logging
import json
import asyncio
from .interface import BaseScrapperExtractor
from ..domain import ScrapePostParams
from .. import config
from .. import exceptions
from ..constants import SupportedBrowersers, SupportedLLMs
from ..domain import CompanyDetail

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
    LLMConfig,
    MemoryAdaptiveDispatcher,
    RateLimiter,
)


class GenericExtractor(BaseScrapperExtractor):
    def __init__(self):
        if not config.GROK_CLOUD_API_KEY:
            raise exceptions.GenericExtractorImproperlyConfiguredException()

        self._api_key = config.GROK_CLOUD_API_KEY
        self._session_id = self._generate_unique_session_id()

    def _get_browser_config(self):
        return BrowserConfig(
            browser_type=SupportedBrowersers.CHROMIUM.value,
            headless=True,
            verbose=True,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        )

    def _get_llm_strategy(self) -> LLMExtractionStrategy:
        return LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider=SupportedLLMs.GROQ_CLOUD_DEEPSEEK_R1.value, api_token=config.GROK_CLOUD_API_KEY
            ),
            schema=CompanyDetail.model_json_schema(),
            extraction_type="schema",
            instructions=(
                "Extract all company objects with 'name', 'domain', 'linkedIn', 'comodity', 'employees count' as size, 'headquaters' as geo"
                "and a 1 sentence description as to why this is a good company for sales reps looking for shipping leads"
            ),
            input_format="markdown",
            verbose=True,
            raise_on_error=True,
        )

    async def crawl_company_information(self, links: ScrapePostParams):
        """Bulk-scrape all URLs in one shot with Crawl4AI’s arun_many()."""
        if not links.scrape_links:
            return []

        urls = [item.company_scrape_link for item in links.scrape_links]
        llm_strategy = self._get_llm_strategy()

        run_cfg = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            session_id=self._session_id,
            stream=True,
        )

        dispatcher = MemoryAdaptiveDispatcher(
            max_session_permit=5,
            rate_limiter=RateLimiter(base_delay=(1.5, 3.0), max_delay=30.0, max_retries=4),
        )

        all_companies = []
        async with AsyncWebCrawler(config=self._get_browser_config()) as crawler:
            async for result in await crawler.arun_many(urls=urls, config=run_cfg, dispatcher=dispatcher):
                if not (result.success and result.extracted_content):
                    logging.error(f"Failed {result.url}: {result.error_message}")
                    continue

                try:
                    companies = json.loads(result.extracted_content)
                except json.JSONDecodeError:
                    logging.warning(f"Bad JSON from {result.url}")
                    continue

                # deals with litellm errors
                if isinstance(companies, list) and self._is_llm_error(companies):
                    logging.error("LLM extraction failed on %s → %s", result.url, companies[0]["content"])
                    continue

                cleaned = [c for c in companies if self._none_empty(c)]
                all_companies.extend(cleaned)

        llm_strategy.show_usage()
        return all_companies

    def _generate_unique_session_id(self, length=32):
        alphabet = string.ascii_letters + string.digits

        key = "".join(secrets.choice(alphabet) for _ in range(length))
        return key

    def _none_empty(self, company_info: typing.Dict[str, typing.Any]) -> bool:
        return any(v not in (None, [], "") for v in company_info.values())

    def _is_llm_error(self, payload: typing.List[typing.Dict[str, typing.Any]]) -> bool:
        return all(isinstance(item, dict) and item.get("error") for item in payload)
