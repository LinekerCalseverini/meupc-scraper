import pytest
from unittest.mock import AsyncMock, MagicMock
from infrastructure.gateways.meupcnet.repos.storage_repo import MeupcnetStorageRepo
from infrastructure.config.settings import ApiConfig
from infrastructure.http.http_client import HttpClient
from domain.entities.products import Storage


@pytest.fixture
def api_config():
    config = MagicMock(spec=ApiConfig)
    config.url = "https://meupc.net"
    return config


@pytest.fixture
def http_client():
    return MagicMock(spec=HttpClient)


@pytest.mark.asyncio
async def test_meupcnet_storage_repo_get_all(api_config, http_client):
    # Setup login response cookies
    login_response = MagicMock()
    login_response.cookies = {
        "ci_csrf_cookie": "csrf_abc",
        "meupcnet": "net_xyz",
    }

    # Setup POST data payload return matching the expected API keys
    raw_storage_data = [
        {
            "descricao": "Samsung 980 PRO 1TB",
            "serie": "980 PRO",
            "formato": "M.2 2280",
            "tipo": "NVMe",
            "capacidade_padrao": 1000,
            "leitura": 7000,
            "gravacao": 5000,
            "slug": "samsung-980-pro-1tb",
            "hash": "abc123hash",
            "preco": 500.00,
            "preco_boleto": 450.00,
            "patrocinado": 0,
            "small": "small.jpg",
            "medium": "medium.jpg",
            "large": "large.jpg",
        }
    ]

    post_response = MagicMock()
    post_response.json.return_value = {"peca": raw_storage_data}

    http_client.get = AsyncMock(return_value=login_response)
    http_client.post = AsyncMock(return_value=post_response)

    # Instantiate storage repository with valid parameters accepted by build_uri_params
    repo = MeupcnetStorageRepo(
        config=api_config, http_client=http_client, params={"capacity_gb_min": 500}
    )

    result = await repo.get_all()

    # Assertions - verifying it correctly parses into the real Storage domain entity
    assert len(result) == 1
    assert isinstance(result[0], Storage)
    assert result[0].hash_ == "abc123hash"
    assert result[0].slug == "samsung-980-pro-1tb"
    assert result[0].capacity_gb == int(1000)
    assert result[0].price_cents == int(50000)  # 500.00 -> 50000 cents
    assert result[0].price_slip_cents == int(45000)  # 450.00 -> 45000 cents

    http_client.get.assert_awaited_once()
    http_client.post.assert_awaited_once()
