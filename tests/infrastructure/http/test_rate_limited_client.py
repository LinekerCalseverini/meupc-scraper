import asyncio

import pytest

from infrastructure.http.rate_limited_client import RateLimitedClient


class MockHttpClient:
    def __init__(self, raise_exc=None):

        self.requests = []

        self.raise_exc = raise_exc

    async def request(self, method, url, **kwargs):

        self.requests.append((method, url, kwargs))

        if self.raise_exc:
            raise self.raise_exc

        return f"Response for {method} {url}"


@pytest.mark.asyncio
async def test_batch_rate_limited_client_methods():

    mock_client = MockHttpClient()

    # Use a very short time window (0.01s) so tests run instantly
    client = RateLimitedClient(
        client=mock_client, requests_per_second=5, time_window=0.01
    )

    # Test all HTTP verb wrapper methods
    assert (
        await client.get("https://example.com/get")
        == "Response for GET https://example.com/get"
    )
    assert (
        await client.post("https://example.com/post", json={"data": 1})
        == "Response for POST https://example.com/post"
    )
    assert (
        await client.put("https://example.com/put")
        == "Response for PUT https://example.com/put"
    )
    assert (
        await client.delete("https://example.com/delete")
        == "Response for DELETE https://example.com/delete"
    )
    assert (
        await client.patch("https://example.com/patch")
        == "Response for PATCH https://example.com/patch"
    )

    assert len(mock_client.requests) == int(5)


@pytest.mark.asyncio
async def test_batch_rate_limited_client_batching():

    mock_client = MockHttpClient()

    # Limit to 3 requests per window, forcing them to span across multiple ticks
    client = RateLimitedClient(
        client=mock_client, requests_per_second=3, time_window=0.01
    )

    # Fire 7 requests concurrently

    tasks = [client.get(f"https://example.com/{i}") for i in range(7)]

    results = await asyncio.gather(*tasks)

    assert len(results) == int(7)

    assert len(mock_client.requests) == int(7)

    for i, res in enumerate(results):
        assert res == f"Response for GET https://example.com/{i}"


@pytest.mark.asyncio
async def test_batch_rate_limited_client_exception_propagation():

    mock_client = MockHttpClient(raise_exc=ValueError("Underlying failure"))
    client = RateLimitedClient(
        client=mock_client, requests_per_second=5, time_window=0.01
    )

    with pytest.raises(ValueError, match="Underlying failure"):
        await client.get("https://example.com/error")
