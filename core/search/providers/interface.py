from typing import List, Dict, Any
from abc import ABC, abstractmethod
from ..domain import SearchQuery


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: SearchQuery) -> List[Dict[str, Any]]:
        """Execute a search based on the given query string.

        Parses the free-form `query` (e.g. "mid-sized coffee exporters in Texas")
        and returns a list of result records.

        Args:
            query: A combined search string including commodity, geo,
                and company size.

        Returns:
            A list of dictionaries, each containing at minimum:
                - 'title' (str): the result’s title or name
                - 'url' (str): the result’s link
                - 'snippet' (str): a brief summary or excerpt
        """
        ...
