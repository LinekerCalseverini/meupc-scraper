from infrastructure.config.settings import ApiConfig
from infrastructure.gateways.meupcnet.adapters.base import (
    build_cookies,
    build_form_token,
    build_headers,
)
from infrastructure.gateways.meupcnet.errors import MeuPCUnexpectedResponseError
from infrastructure.http.http_client import HttpClient


class MeuPCAuthMixin:
    """Mixin responsible for managing session cookies, CSRF tokens, and login state."""

    def __init__(self, config: ApiConfig, http_client: HttpClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http_client = http_client
        self._url = config.url
        self._path = ""

        # Session State
        self._logged_in = False
        self._csrf_token: str | None = None
        self._meupc_token: str | None = None
        self._cookies: dict | None = None
        self._form_token: bytes | None = None

    async def _ensure_logged_in(self) -> None:
        """
        Captures cookies and tokens from the base API URL if not already logged in.
        """
        if not self._logged_in:
            response = await self._http_client.get(self._url)

            self._csrf_token = response.cookies.get("ci_csrf_cookie")
            if not self._csrf_token:
                raise MeuPCUnexpectedResponseError("Missing ci_csrf_cookie")

            self._meupc_token = response.cookies.get("meupcnet")
            if not self._meupc_token:
                raise MeuPCUnexpectedResponseError("Missing meupcnet cookie")

            self._cookies = build_cookies(self._csrf_token, self._meupc_token)
            self._form_token = build_form_token(self._csrf_token)
            self._headers = build_headers(self._path)
            self._logged_in = True
