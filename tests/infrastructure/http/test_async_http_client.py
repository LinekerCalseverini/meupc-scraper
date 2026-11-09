import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import TimeoutException, TransportError, HTTPStatusError, Request, Response

from infrastructure.http.async_http_client import AsyncHttpClient
from infrastructure.http.errors import (
    HttpClientRetryError,
    HttpClientTimeoutError,
    HttpClientError,
)

EXPECTED_ATTEMPTS_SUCCESS = 2
EXPECTED_ATTEMPTS_EXHAUSTED = 3


@pytest.fixture
def client_factory():
    def _create(
        side_effect: list | None = None, raise_on_status: Exception | None = None
    ):
        mock_client = MagicMock()
        mock_request = AsyncMock()

        if side_effect:
            mock_request.side_effect = side_effect
        else:
            mock_response = MagicMock()
            if raise_on_status:
                mock_response.raise_for_status.side_effect = raise_on_status
            mock_request.return_value = mock_response

        mock_client.request = mock_request
        return AsyncHttpClient(timeout=1, retries=3, backoff=0, client=mock_client)

    return _create


@pytest.mark.parametrize("method", ["get", "post", "put", "delete", "patch"])
async def test_async_http_client_methods(client_factory, method):
    client = client_factory()
    await getattr(client, method)("https://example.com")

    mock_client = client._client
    mock_client.request.assert_awaited_once()
    args, _ = mock_client.request.call_args
    assert args[0] == method.upper()
    assert args[1] == "https://example.com"


@pytest.mark.parametrize("exc_class", [TimeoutException, TransportError, EOFError])
async def test_async_http_client_retries_and_succeeds(client_factory, exc_class):
    # Fail the first attempt with an exception, succeed on the second with a mock
    # response
    mock_response = MagicMock()
    client = client_factory(side_effect=[exc_class("Transient error"), mock_response])

    response = await client.get("https://example.com")

    assert response is not None
    assert client._client.request.call_count == EXPECTED_ATTEMPTS_SUCCESS
    args, _ = client._client.request.call_args
    assert args[0] == "GET"


@pytest.mark.parametrize("exc_class", [TimeoutException, TransportError, EOFError])
async def test_async_http_client_exhausts_retries(client_factory, exc_class):
    # Fail all attempts (retries=3 means 3 attempts total)
    client = client_factory(side_effect=[exc_class("Persistent error")] * 3)

    with pytest.raises(HttpClientRetryError) as exc_info:
        await client.get("https://example.com")

    assert client._client.request.call_count == EXPECTED_ATTEMPTS_EXHAUSTED

    # TimeoutException gets mapped to HttpClientTimeoutError, others keep their type
    if exc_class is TimeoutException:
        assert isinstance(exc_info.value.__cause__, HttpClientTimeoutError)
    else:
        assert isinstance(exc_info.value.__cause__, exc_class)


@pytest.mark.parametrize(
    "exc_instance",
    [
        ValueError("Bad Request"),
        HTTPStatusError(
            "Error",
            request=Request("GET", "https://example.com"),
            response=Response(400),
        ),
    ],
)
async def test_async_http_client_does_not_retry_on_non_retriable_errors(
    client_factory, exc_instance
):
    if isinstance(exc_instance, HTTPStatusError):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = exc_instance
        client = client_factory(side_effect=[mock_response])
    else:
        client = client_factory(side_effect=[exc_instance])

    with pytest.raises(HttpClientError):
        await client.get("https://example.com")

    # Verify it failed on the very first try and did not loop/retry
    assert client._client.request.call_count == 1
