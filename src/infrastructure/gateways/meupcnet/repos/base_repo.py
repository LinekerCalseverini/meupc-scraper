from collections.abc import AsyncIterator, Callable
from typing import Generic, Sequence

from domain.interfaces.product_repo import ProductRepo, T
from infrastructure.config.settings import ApiConfig
from infrastructure.gateways.meupcnet.auth import MeuPCAuthMixin
from infrastructure.http.http_client import HttpClient


class MeuPCApiError(Exception):
    pass


class MeuPCUnexpectedResponseError(MeuPCApiError):
    def __init__(self, response):
        super().__init__(f"Unexpected response from MeuPC API: {response}")


class BaseRepo(MeuPCAuthMixin, ProductRepo[T], Generic[T]):
    def __init__(
        self,
        config: ApiConfig,
        http_client: HttpClient,
        adapter: Callable[[list[dict]], list[T]],
        params: dict | None = None,
    ):
        # Passes config and http_client up the MRO (Method Resolution Order)
        super().__init__(config=config, http_client=http_client)

        self._params = params
        self._adapter = adapter

    async def get_all(self) -> AsyncIterator[T]:
        # Ensure login happens before building headers/payloads
        await self._ensure_logged_in()

        clean_path = self._path.strip("/")

        payload = {
            "url": f"{self._url}/api/{clean_path}",
            "cookies": self._cookies,
            "headers": self._headers,
            "content": self._form_token,
        }

        if self._params:
            payload["params"] = self._params.copy()
        else:
            payload["params"] = {}

        # 1. Fetch page 1 first to get the total count
        payload["params"]["page"] = 1
        response = await self._http_client.post(**payload)
        response_json = response.json()
        response_count = int(response_json.get("total", 0))

        # Yield items from page 1
        for entity in self._adapter(response_json.get("peca", [])):
            yield entity

        if response_count <= 0:
            return

        # 2. Calculate total pages (e.g., 2000 / 50 = 40 pages total)
        page_size = 50
        total_pages = (response_count + page_size - 1) // page_size

        # 3. Loop through remaining pages sequentially (2 to 40)
        for page in range(2, total_pages + 1):
            payload["params"]["page"] = page
            response = await self._http_client.post(**payload)
            response_json = response.json()

            for entity in self._adapter(response_json.get("peca", [])):
                yield entity

    async def add(self, entity: T) -> None:
        return

    async def add_many(self, entities: Sequence[T]) -> None:
        return
