from pydantic import BaseModel
import typing
from .constants import Extractors


class _CompanyScrapeInfo(BaseModel):
    company_name: str
    company_scrape_link: str


class ScrapePostParams(BaseModel):
    extractor: typing.Optional[str] = Extractors.GENERIC.value
    scrape_links: typing.List[_CompanyScrapeInfo]


class CompanyDetail(BaseModel):
    domain: typing.Optional[str] = None
    linkedIn: typing.Optional[str] = None
    name: typing.Optional[str] = None
    description: typing.Optional[str] = None
    commodity: typing.Optional[typing.Union[str, typing.List[str]]] = None
    size: typing.Optional[str] = None
    geo: typing.Optional[str] = None  # this is the city they operate from or headquatered.
