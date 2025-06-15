import requests
import typing

from .. import exceptions
from .. import config


class GoogleSearchAPIClient:
    BASE_URL = config.GOOGLE_CUSTOM_SEARCH_BASE_URL
    MAX_RETRIES = 2
    RETRY_TIME = 10  # time in seconds to wait to retry the request.

    def __init__(self, api_key: str, cx: str, timeout: float = 8.0):
        self.api_key = api_key
        self.cx = cx
        self.timeout = timeout
        self.session: typing.Optional[requests.Session] = None

    def __enter__(self) -> "GoogleSearchAPIClient":
        self.session = requests.Session()
        return self

    def __exit__(self, *_):
        if self.session is not None:
            self.session.close()
            self.session = None

    def fetch(self, params: typing.Dict[str, typing.Any]) -> typing.Dict:
        if self.session is None:
            with requests.Session() as temp_session:
                return self._do_fetch(temp_session, params)
        return self._do_fetch(self.session, params)

    def _do_fetch(
        self,
        session: requests.Session,
        params: typing.Dict[str, typing.Any],
        retries: int = 0,
        prev_exception: typing.Optional[Exception] = None,
    ) -> typing.Dict[str, typing.Any]:
        if retries > self.MAX_RETRIES:
            raise prev_exception or exceptions.GoogleHTTPError(503, "Max retries exceeded")

        payload = {**params, "key": self.api_key, "cx": self.cx}

        try:
            resp = session.get(self.BASE_URL, params=payload, timeout=self.timeout)
        except requests.exceptions.RequestException as network_error:
            return self._do_fetch(session, params, retries=retries + 1, prev_exception=network_error)

        if resp.status_code in (
            401,
            403,
        ):
            raise exceptions.GoogleAuthError()

        if resp.status_code == 429:
            raise exceptions.GoogleQuotaExceeded()

        if resp.status_code >= 400:
            detail = ""
            try:
                detail = resp.json().get("error", {}).get("message", resp.text)
            except ValueError:
                detail = resp.text
            raise exceptions.GoogleHTTPError(resp.status_code, detail)

        return resp.json()
