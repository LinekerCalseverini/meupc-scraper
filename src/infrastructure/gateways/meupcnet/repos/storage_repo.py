from typing import Callable
from domain.entities.products import Storage

from infrastructure.gateways.meupcnet.repos.base_repo import BaseRepo
from infrastructure.http.http_client import HttpClient
from infrastructure.config.settings import ApiConfig

from infrastructure.gateways.meupcnet.adapters.storage import (
    to_domain_storage_many,
    build_uri_params,
)


class MeupcnetStorageRepo(BaseRepo[Storage]):
    def __init__(
        self,
        config: ApiConfig,
        http_client: HttpClient,
        params: dict | None = None,
        adapter: Callable[[list[dict]], list[Storage]] = to_domain_storage_many,
    ):
        safe_params = build_uri_params(**(params or {}))
        super().__init__(
            config,
            http_client,
            adapter=adapter,
            params=safe_params,
        )
        self._url = f"{self._url}/armazenamentos"
        self._path = f"{self._path}/armazenamentos"
