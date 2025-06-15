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

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, LLMExtractionStrategy, LLMConfig


class GenericExtractor(BaseScrapperExtractor):
    def __init__(self):
        if not config.GROK_CLOUD_API_KEY:
            raise exceptions.GenericExtractorImproperlyConfiguredException()

        self._api_key = config.GROK_CLOUD_API_KEY
        self._session_id = self._generate_unique_session_id()

    def _get_browser_config(self):
        return BrowserConfig(
            browser_type=SupportedBrowersers.CHROMIUM.value,  # type of browsers to simulate
            headless=True,  # Whether to run in headless mode (no GUI)
            verbose=True,  # capture as much logs of the process as much as possible
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        )

    def _get_llm_strategy(self):
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
            verbose=True,  # enable verbose logging.
        )

    async def crawl_company_information(self, links_to_scrape: ScrapePostParams):
        all_companies = []

        if not links_to_scrape.scrape_links:
            return all_companies

        llm_strategy = self._get_llm_strategy()

        async with AsyncWebCrawler(config=self._get_browser_config()) as crawler:
            for company_scrape_info in links_to_scrape.scrape_links or []:

                company_info = await self._fetch_and_crawl_page(
                    crawler=crawler,
                    url=company_scrape_info.company_scrape_link,
                    llm_strategy=self._get_llm_strategy(),
                    session_id=self._session_id,
                )

                if not company_info:
                    logging.info(
                        f"No information for available for this site: {company_scrape_info.company_scrape_link}"
                    )
                    continue

                all_companies.extend(company_info)
                # pause between requests to avoid rate limits
                await asyncio.sleep(2)

        llm_strategy.show_usage()
        return all_companies

    async def _fetch_and_crawl_page(self, crawler, url, llm_strategy, session_id) -> typing.List[typing.Any]:
        try:
            result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS, extraction_strategy=llm_strategy, session_id=session_id
                ),
            )

            if not (result.success and result.extracted_content):
                logging.error(f"Error fetching page: {result.error_message}")
                return []

            extracted_data = json.loads(result.extracted_content)
            if not extracted_data:
                logging.info("No company information found")
                return []

            return extracted_data
        except Exception as e:
            logging.error(f"Error scraping page: {str(e)}")
            return []

    def _generate_unique_session_id(self, length=32):
        alphabet = string.ascii_letters + string.digits

        key = "".join(secrets.choice(alphabet) for _ in range(length))
        return key
