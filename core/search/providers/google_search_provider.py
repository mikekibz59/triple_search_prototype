import logging
import typing
from ..domain import SearchQuery, SearchResult
from .interface import SearchProvider
from ..http.google_search_client import GoogleSearchAPIClient
from .. import config
from .. import exceptions


class GoogleSearchProvider(SearchProvider):
    """Google Custom Search implementation"""

    DEFAULT_COUNTRY = "us"

    def __init__(self):
        if not config.GOOGLE_API_KEY or not config.GOOGLE_CX:
            raise exceptions.GoogleAuthError()
        self._api_key = config.GOOGLE_API_KEY
        self._cx = config.GOOGLE_CX
        self._max_pages = int(config.GOOGLE_QUERY_MAX_PAGES)
        self._num_results = 2

    def _build_params(self, query: SearchQuery, page: int) -> typing.Dict[str, typing.Any]:
        terms = [
            '(intitle:about OR inurl:about OR intitle:"company profile")',
            'shipping',
            '-jobs -careers -hiring',
            '-filetype:pdf -filetype:xlsx -filetype:csv'
        ]
        if query.commodity:
            terms.append(f'"{query.commodity}"')
        if query.geo:
            terms.append(f'"{query.geo}"')
        if query.company_size:
            terms.append(f'"{query.company_size}"')

        query_string = " ".join(terms)

        return {
            "q": query_string,
            "num": self._num_results,
            "start": page,
            "gl": "us",
            "fields": "items(link, title, snippet), queries(nextPage/startIndex)",
        }

    def search(self, query: SearchQuery) -> list[SearchResult]:
        results: list[SearchResult] = []
        partial = False  # track if we bailed early

        with GoogleSearchAPIClient(self._api_key, self._cx) as api_client:
            start = 1
            for _ in range(self._max_pages):
                try:
                    raw = api_client.fetch(self._build_params(query, start))
                except exceptions.GoogleQuotaExceeded as e:
                    logging.error("Quota hit: %s", e)
                    partial = True
                    break
                except exceptions.GoogleAuthError as e:
                    logging.error("Auth error: %s", e)
                    raise e
                except exceptions.GoogleHTTPError as e:
                    logging.warning("Page fetch failed, skipping: %s", e)
                    partial = True
                    break

                for rank, item in enumerate(raw.get("items", []), start=start):
                    results.append(
                        SearchResult(
                            title=item["title"],
                            url=item["link"],
                            snippet=item.get("snippet", ""),
                            source_url=item["link"],
                            matched_terms=[query.commodity, query.geo, query.company_size],
                            score=rank,
                        )
                    )
                next_pages = raw.get("queries", {}).get("nextPage", [])
                if not next_pages:
                    break
                start = next_pages[0]["startIndex"]

        logging.info(
            "GoogleSearchProvider fetched %d result(s)%s for %s", len(results), " (partial)" if partial else "", query
        )

        return results
