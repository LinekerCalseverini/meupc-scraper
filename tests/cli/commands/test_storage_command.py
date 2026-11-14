import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from cli.commands.storage import sync_storage, sync_storage_prices


def test_sync_storage_command() -> None:
    mock_config = SimpleNamespace(
        api=MagicMock(),
        http=SimpleNamespace(timeout=10, retries=3),
    )

    with (
        patch(
            "cli.commands.storage.YamlConfigLoader.load",
            new_callable=AsyncMock,
            return_value=mock_config,
        ) as mock_load,
        patch("cli.commands.storage.LocalDatabase") as mock_db_cls,
        patch("cli.commands.storage.MeupcnetStorageRepo") as mock_remote_cls,
        patch("cli.commands.storage.LocalStorageRepo") as mock_local_cls,
        patch("cli.commands.storage.SyncReposUseCase") as mock_use_case_cls,
    ):
        mock_execute = AsyncMock()
        mock_use_case_cls.return_value.execute = mock_execute

        asyncio.run(sync_storage(config_path="custom_config.yaml"))

        mock_load.assert_awaited_once()
        mock_db_cls.return_value.get_session.assert_called_once()
        mock_remote_cls.assert_called_once()
        mock_local_cls.assert_called_once()
        mock_execute.assert_awaited_once()


def test_sync_storage_prices_command() -> None:
    mock_config = SimpleNamespace(
        api=MagicMock(),
        http=SimpleNamespace(timeout=10, retries=3, rate_limit=5),
    )

    mock_remote_instance = AsyncMock()
    mock_remote_instance.__aenter__.return_value = mock_remote_instance
    mock_remote_instance.__aexit__.return_value = None

    with (
        patch(
            "cli.commands.storage.YamlConfigLoader.load",
            new_callable=AsyncMock,
            return_value=mock_config,
        ) as mock_load,
        patch("cli.commands.storage.LocalDatabase") as mock_db_cls,
        patch(
            "cli.commands.storage.MeupcnetPriceHistoryRepo",
            return_value=mock_remote_instance,
        ) as mock_remote_cls,
        patch("cli.commands.storage.PriceHistoryRepo") as mock_local_cls,
        patch("cli.commands.storage.LocalStorageRepo") as mock_storage_repo_cls,
        patch("cli.commands.storage.SyncPriceHistoryUseCase") as mock_use_case_cls,
    ):
        mock_execute = AsyncMock()
        mock_use_case_cls.return_value.execute = mock_execute

        asyncio.run(sync_storage_prices(config_path="custom_config.yaml"))

        mock_load.assert_awaited_once()
        assert mock_db_cls.return_value.get_session.call_count >= 1
        mock_remote_cls.assert_called_once()
        mock_local_cls.assert_called_once()
        mock_storage_repo_cls.assert_called_once()
        mock_execute.assert_awaited_once()
