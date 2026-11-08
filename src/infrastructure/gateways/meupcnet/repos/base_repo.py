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


class BaseRepo(Repository, Generic[T]):
    def __init__(
        self,
        config: ApiConfig,
        http_client: HttpClient,
        single_adapter: Callable[[dict], T],
        many_adapter: Callable[[list[dict]], list[T]],
        params: dict | None = None,
    ):
        self._http_client = http_client
        self._url = f"{config.url}/api"
        self._csrf_token = config.csrf_token
        self._meupc_token = config.meupc_token
        self._headers = build_headers()
        self._cookies = build_cookies(self._csrf_token, self._meupc_token)
        self._form_token = build_form_token(self._csrf_token)
        self._params = params
        self._single_adapter = single_adapter
        self._many_adapter = many_adapter

    async def get_all(self) -> list[T]:
        payload = {
            "url": self._url,
            "cookies": self._cookies,
            "headers": self._headers,
            "content": self._form_token,
        }
        if self._params:
            payload["params"] = self._params
        return self._many_adapter(await self._http_client.post(**payload))
