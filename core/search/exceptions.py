from typing import Optional


class GoogleSearchException(Exception):
    """Base class for all Google search-related errors."""


class GoogleAuthError(GoogleSearchException):
    message = "Missing or invalid API key / CX ID."
    http_status = 401

    def __init__(self):
        super().__init__(self.message)


class GoogleQuotaExceeded(GoogleSearchException):
    message = "Google Custom Search quota exceeded"
    http_status = 429

    def __init__(self, custom_msg: Optional[str] = None):
        super().__init__(custom_msg or self.message)


class GoogleHTTPError(GoogleSearchException):
    def __init__(self, status_code: int, detail: str):
        self.http_status = 503 if 500 <= status_code < 600 else 502
        super().__init__(detail)


class SearchServiceException(Exception):
    pass
