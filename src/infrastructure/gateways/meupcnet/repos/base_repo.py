from collections.abc import Callable

from typing import Generic, TypeVar


from domain.interfaces.product_repo import Repository


from infrastructure.http.http_client import HttpClient

from infrastructure.config.settings import ApiConfig


from infrastructure.gateways.meupcnet.adapters.base import (
    build_headers,
    build_cookies,
    build_form_token,
)


T = TypeVar("T")


class MeuPCApiError(Exception):
    pass


class MeuPCUnexpectedResponseError(MeuPCApiError):
    # base message = "Unexpected response from MeuPC API: {response}"
    def __init__(self, response):
        super().__init__(f"Unexpected response from MeuPC API: {response}")


class BaseRepo(Repository, Generic[T]):
    def __init__(
        self,
        config: ApiConfig,
        http_client: HttpClient,
        adapter: Callable[[list[dict]], list[T]],
        params: dict | None = None,
    ):
        self._http_client = http_client
        self._url = config.url
        self._path = ""

        # Session
        self._logged_in = False
        self._csrf_token = None
        self._meupc_token = None

        # Request
        self._headers = {}
        self._cookies = None
        self._form_token = None
        self._params = params
        self._adapter = adapter

    async def _ensure_logged_in(self):
        """
        Captures ci_csrf_cookie and meupcnet from the Set-Cookie header
        After sending a get request to the base API url
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
            self._logged_in = True

    async def get_all(self) -> list[T]:
        # Ensure login happens before building headers/payloads
        await self._ensure_logged_in()

        self._headers = build_headers(self._path)

        # Keep URL clean: e.g., {self._url}/api/{self._path}
        # Ensure self._path doesn't have leading/trailing double slashes
        clean_path = self._path.strip("/")
        payload = {
            "url": f"{self._url}/api/{clean_path}",
            "cookies": self._cookies,
            "headers": self._headers,
            "content": self._form_token,
        }

        if self._params:
            payload["params"] = self._params

        response = await self._http_client.post(**payload)
        return self._adapter(response.json().get("peca", []))

    async def add(self, entity: T) -> None:
        return

    async def add_many(self, entities: list[T]) -> None:
        return
