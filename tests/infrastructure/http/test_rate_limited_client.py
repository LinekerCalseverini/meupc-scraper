import asyncio
from unittest.mock import AsyncMock
import pytest

from infrastructure.http.rate_limited_client import RateLimitedClient

TOTAL_BATCH_REQUESTS = 7


@pytest.fixture
def rate_limited_client_factory():
    def _create(side_effect=None):
        mock_client = AsyncMock()
        if side_effect:
            mock_client.request.side_effect = side_effect
        else:
            mock_client.request.side_effect = lambda method, url, **kwargs: (
                f"Response for {method} {url}"
            )

        return RateLimitedClient(
            client=mock_client, requests_per_second=5, time_window=0.01
        )

    return _create


@pytest.mark.parametrize("method", ["get", "post", "put", "delete", "patch"])
async def test_rate_limited_client_method(rate_limited_client_factory, method):
    client = rate_limited_client_factory()
    url = f"https://example.com/{method}"

    if method == "post":
        response = await getattr(client, method)(url, json={"data": 1})
    else:
        response = await getattr(client, method)(url)

    assert response == f"Response for {method.upper()} {url}"
    client._client.request.assert_awaited_once()


async def test_rate_limited_client_batching(rate_limited_client_factory):
    client = rate_limited_client_factory()

    # Fire 7 requests concurrently, limiting to 3 requests per window
    tasks = [
        client.get(f"https://example.com/{i}") for i in range(TOTAL_BATCH_REQUESTS)
    ]
    results = await asyncio.gather(*tasks)

    assert len(results) == TOTAL_BATCH_REQUESTS
    assert client._client.request.await_count == TOTAL_BATCH_REQUESTS

    for i, res in enumerate(results):
        assert res == f"Response for GET https://example.com/{i}"


async def test_rate_limited_client_exception_propagation(rate_limited_client_factory):
    client = rate_limited_client_factory(side_effect=ValueError("Underlying failure"))

    with pytest.raises(ValueError, match="Underlying failure"):
        await client.get("https://example.com/error")
