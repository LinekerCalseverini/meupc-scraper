from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from typer.testing import CliRunner

from cli.commands.storage import storage


def test_sync_storage_command() -> None:
    runner = CliRunner()

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

        result = runner.invoke(storage, ["--config-path", "custom_config.yaml"])

        assert result.exit_code == 0
        mock_load.assert_awaited_once()
        mock_db_cls.return_value.get_session.assert_called_once()
        mock_remote_cls.assert_called_once()
        mock_local_cls.assert_called_once()
        mock_execute.assert_awaited_once()
