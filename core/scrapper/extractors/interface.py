from abc import ABC, abstractmethod
import typing
from ..domain import CompanyDetail, ScrapePostParams
from crawl4ai import BrowserConfig, LLMExtractionStrategy, AsyncWebCrawler


class BaseScrapperExtractor(ABC):
    @abstractmethod
    def _get_browser_config(self) -> BrowserConfig: ...

    @abstractmethod
    def _get_llm_strategy(self) -> LLMExtractionStrategy:
        """Returns teh configuration for the language model extraction strategy

        Returns:
            LLMExtractionStrategy: The settings for how to extract data using LLM.
        """

    @abstractmethod
    async def _fetch_and_crawl_page(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        llm_strategy: LLMExtractionStrategy,
        session_id: str,
    ) -> typing.List[typing.Any]:
        """
        Fetches and processes a single page of company data
        Args:
            crawler (AsyncWebCrawler): The web crawler instance.
            page_number (int): The page number to fetch.
            base_url (str): The base URL of the website.
            llm_strategy (LLMExtractionStrategy): The LLM extraction strategy.
            session_id (str): The session identifier.

        Returns:
            typing.List: Results from scrapping the page
        """

    @abstractmethod
    async def crawl_company_information(self, links_to_scrape: ScrapePostParams)-> typing.List[CompanyDetail]:
        """main method to crawl company data from the website."""


    @abstractmethod
    def _generate_unique_session_id(self, length=32) -> str:
        """Generates a secure random key of the specified length."""
        ...
