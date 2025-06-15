import typing
from .extractors.generic_extractor import GenericExtractor
from .extractors.interface import BaseScrapperExtractor
from .constants import Extractors


def get_extractor(name: typing.Optional[str] = None) -> BaseScrapperExtractor:
    generic_extractor_constant = Extractors.GENERIC.value
    name = (name or generic_extractor_constant).lower()
    if name == generic_extractor_constant:
        return GenericExtractor
    raise ValueError(f"Unkown extractor {name}")
