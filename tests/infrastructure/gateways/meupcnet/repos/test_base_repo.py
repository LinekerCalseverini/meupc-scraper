import pytest
from unittest.mock import AsyncMock, MagicMock
from infrastructure.gateways.meupcnet.repos.base_repo import (
    BaseRepo,
    MeuPCUnexpectedResponseError,
)
from infrastructure.config.settings import ApiConfig
from infrastructure.http.http_client import HttpClient


@pytest.fixture
def api_config():
    config = MagicMock(spec=ApiConfig)
    config.url = "https://meupc.net"
    return config


@pytest.fixture
def http_client():
    return MagicMock(spec=HttpClient)


@pytest.fixture
def sample_adapter():
    return lambda data: [item["id"] for item in data]


@pytest.mark.asyncio
async def test_ensure_logged_in_success(api_config, http_client, sample_adapter):
    mock_response = MagicMock()
    mock_response.cookies = {
        "ci_csrf_cookie": "dummy_csrf_token",
        "meupcnet": "dummy_meupcnet_token",
    }
    http_client.get = AsyncMock(return_value=mock_response)

    repo = BaseRepo(api_config, http_client, sample_adapter)
    await repo._ensure_logged_in()

    assert repo._logged_in is True
    assert repo._csrf_token == "dummy_csrf_token"
    assert repo._meupc_token == "dummy_meupcnet_token"
    http_client.get.assert_awaited_once_with("https://meupc.net")


@pytest.mark.asyncio
async def test_ensure_logged_in_missing_cookie(api_config, http_client, sample_adapter):
    mock_response = MagicMock()
    mock_response.cookies = {"ci_csrf_cookie": "dummy_csrf_token"}
    http_client.get = AsyncMock(return_value=mock_response)

    repo = BaseRepo(api_config, http_client, sample_adapter)

    with pytest.raises(MeuPCUnexpectedResponseError, match="Missing meupcnet cookie"):
        await repo._ensure_logged_in()


@pytest.mark.asyncio
async def test_get_all_success(api_config, http_client, sample_adapter):
    login_response = MagicMock()
    login_response.cookies = {
        "ci_csrf_cookie": "csrf_123",
        "meupcnet": "net_456",
    }

    post_response = MagicMock()
    post_response.json.return_value = {"peca": [{"id": 10}, {"id": 20}]}

    http_client.get = AsyncMock(return_value=login_response)
    http_client.post = AsyncMock(return_value=post_response)

    repo = BaseRepo(api_config, http_client, sample_adapter)
    repo._path = "test-path"

    result = [item async for item in repo.get_all()]

    assert result == [10, 20]
    http_client.get.assert_awaited_once()
    http_client.post.assert_awaited_once()
