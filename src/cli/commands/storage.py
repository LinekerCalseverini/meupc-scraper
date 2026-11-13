from async_typer import AsyncTyper

from use_cases.sync_repos import SyncReposUseCase
from infrastructure.gateways.meupc_localdb.repos.storage_repo import LocalStorageRepo
from infrastructure.gateways.meupc_localdb.database import LocalDatabase
from infrastructure.gateways.meupcnet.repos.storage_repo import MeupcnetStorageRepo
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
