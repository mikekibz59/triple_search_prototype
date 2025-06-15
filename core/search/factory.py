import typing
from .providers.google_search_provider import GoogleSearchProvider
from .providers.interface import SearchProvider


def get_provider(name: typing.Optional[str] = None) -> SearchProvider:
    name = (name or "google").lower()
    if name == "google":
        return GoogleSearchProvider
    raise ValueError(f"Unkown search provider {name}")
