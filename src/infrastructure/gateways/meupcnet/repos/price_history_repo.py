import logging

from domain.entities.dataseries import DataPoint
from domain.interfaces.dataseries_repo import DataSeriesRepo
from infrastructure.gateways.meupcnet.auth import MeuPCAuthMixin
from infrastructure.http.http_client import HttpClient
from infrastructure.config.settings import ApiConfig
from infrastructure.gateways.meupcnet.adapters.price_history import (
    build_uri_params,
    to_dataseries,
)
from infrastructure.gateways.meupcnet.models.price_history import (
    PriceHistoryApiResponseModel,
)


logger = logging.getLogger(__name__)


class MeupcnetPriceHistoryRepo(MeuPCAuthMixin, DataSeriesRepo):
    def __init__(self, config: ApiConfig, http_client: HttpClient, *args, **kwargs):
        super().__init__(config, http_client, *args, **kwargs)
        self._path = "historico"

    async def __aenter__(self):
        await self._ensure_logged_in()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return

    async def get_history(self, sku_hash: str) -> list[DataPoint]:
        await self._ensure_logged_in()

        clean_path = self._path.strip("/")
        safe_params = build_uri_params(sku_hash=sku_hash)

        payload = {
            "url": f"{self._url}/api/{clean_path}",
            "cookies": self._cookies,
            "headers": self._headers,
            "content": self._form_token,
            "params": safe_params,
        }

        response = await self._http_client.post(**payload)
        response_json = response.json()
        if not response_json.get("datasets", []):
            return []

        try:
            price_response = PriceHistoryApiResponseModel(**response_json)
        except Exception as e:
            logger.error({"response": response_json, "error": e})
            return []

        return to_dataseries(sku_hash=sku_hash, price_history=price_response)

    async def add_history(self, history: list[DataPoint]) -> None:
        return
