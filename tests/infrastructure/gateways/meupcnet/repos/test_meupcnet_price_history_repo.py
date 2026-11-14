import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from infrastructure.gateways.meupcnet.repos.price_history_repo import (
    MeupcnetPriceHistoryRepo,
)
from infrastructure.config.settings import ApiConfig

EXPECTED_PRICE_CENTS = 1000


@pytest.mark.asyncio
async def test_meupcnet_price_history_repo_lifecycle():
    config = MagicMock(spec=ApiConfig)
    config.url = "http://localhost"
    http_client = AsyncMock()

    repo = MeupcnetPriceHistoryRepo(config=config, http_client=http_client)

    with patch.object(repo, "_ensure_logged_in", new_callable=AsyncMock) as mock_login:
        async with repo as r:
            assert r is repo
            mock_login.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_history_success():
    config = MagicMock(spec=ApiConfig)
    config.url = "http://localhost"
    http_client = AsyncMock()

    response_mock = MagicMock()
    response_mock.json.return_value = {
        "labels": ["2026-01-01"],
        "datasets": [{"label": "p", "data": [10.0]}],
    }
    http_client.post.return_value = response_mock

    repo = MeupcnetPriceHistoryRepo(config=config, http_client=http_client)
    repo._cookies = {}
    repo._headers = {}
    repo._form_token = b"token"

    with patch.object(repo, "_ensure_logged_in", new_callable=AsyncMock):
        history = await repo.get_history("abc")
        assert len(history) == 1
        assert history[0].value == EXPECTED_PRICE_CENTS


@pytest.mark.asyncio
async def test_get_history_empty_datasets():
    config = MagicMock(spec=ApiConfig)
    config.url = "http://localhost"
    http_client = AsyncMock()

    response_mock = MagicMock()
    response_mock.json.return_value = {"datasets": []}
    http_client.post.return_value = response_mock

    repo = MeupcnetPriceHistoryRepo(config=config, http_client=http_client)
    repo._cookies = {}
    repo._headers = {}
    repo._form_token = b"token"

    with patch.object(repo, "_ensure_logged_in", new_callable=AsyncMock):
        history = await repo.get_history("abc")
        assert history == []


@pytest.mark.asyncio
async def test_get_history_exception():
    config = MagicMock(spec=ApiConfig)
    config.url = "http://localhost"
    http_client = AsyncMock()

    response_mock = MagicMock()
    response_mock.json.return_value = {
        "labels": "invalid-not-list",
        "datasets": [{"label": "p", "data": [10.0]}],
    }
    http_client.post.return_value = response_mock

    repo = MeupcnetPriceHistoryRepo(config=config, http_client=http_client)
    repo._cookies = {}
    repo._headers = {}
    repo._form_token = b"token"

    with patch.object(repo, "_ensure_logged_in", new_callable=AsyncMock):
        history = await repo.get_history("abc")
        assert history == []

        await repo.add_history([])
