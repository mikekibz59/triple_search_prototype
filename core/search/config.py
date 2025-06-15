import os

GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CX: str = os.getenv("GOOGLE_CX", "")
GOOGLE_QUERY_MAX_PAGES: int = int(os.getenv("GOOGLE_QUERY_MAX_PAGES", "2"))
GOOGLE_CUSTOM_SEARCH_BASE_URL: str = os.getenv(
    "GOOGLE_CUSTOM_SEARCH_BASE_URL", "https://www.googleapis.com/customsearch/v1"
)
