from async_typer import AsyncTyper

from use_cases.sync_repos import SyncReposUseCase
from use_cases.sync_price_history import SyncPriceHistoryUseCase
from infrastructure.gateways.meupc_localdb.repos.storage_repo import LocalStorageRepo
from infrastructure.gateways.meupc_localdb.repos.price_history_repo import (
    PriceHistoryRepo,
)
from infrastructure.gateways.meupc_localdb.database import LocalDatabase
from infrastructure.gateways.meupcnet.repos.storage_repo import MeupcnetStorageRepo
from infrastructure.gateways.meupcnet.repos.price_history_repo import (
    MeupcnetPriceHistoryRepo,
)
from infrastructure.config.loaders.yaml import YamlConfigLoader
from infrastructure.http.async_http_client import AsyncHttpClient
from infrastructure.http.rate_limited_client import RateLimitedClient

storage = AsyncTyper(name="storage", help="Manage storage products.")


@storage.command(name="sync")
async def sync_storage(config_path: str = "config.yaml") -> None:
    config = await YamlConfigLoader(path=config_path).load()
    remote_repo = MeupcnetStorageRepo(
        config=config.api,
        http_client=AsyncHttpClient(
            timeout=config.http.timeout,
            retries=config.http.retries,
        ),
    )
    local_repo = LocalStorageRepo(session=LocalDatabase().get_session())

    await SyncReposUseCase(source_repo=remote_repo, target_repo=local_repo).execute()


@storage.command(name="sync-prices")
async def sync_storage_prices(config_path: str = "config.yaml") -> None:
    config = await YamlConfigLoader(path=config_path).load()
    remote_repo = MeupcnetPriceHistoryRepo(
        config=config.api,
        http_client=RateLimitedClient(
            AsyncHttpClient(
                timeout=config.http.timeout,
                retries=config.http.retries,
            ),
            requests_per_second=config.http.rate_limit,
        ),
    )
    local_repo = PriceHistoryRepo(session=LocalDatabase().get_session())
    storage_repo = LocalStorageRepo(session=LocalDatabase().get_session())

    async with remote_repo as remote:
        await SyncPriceHistoryUseCase(
            product_repo=storage_repo,
            source_repo=remote,
            target_repo=local_repo,
        ).execute()
