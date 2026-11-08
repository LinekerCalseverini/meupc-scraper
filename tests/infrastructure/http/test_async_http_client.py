import pytest
from httpx import TimeoutException, TransportError, HTTPStatusError, Request, Response

from infrastructure.http.async_http_client import AsyncHttpClient
from infrastructure.http.errors import (
    HttpClientRetryError,
    HttpClientTimeoutError,
    HttpClientError,
)


def generate_mock_client(
    raise_exc_sequence: list, raise_on_status: Exception | None = None
) -> AsyncHttpClient:
    class MockResponse:
        def raise_for_status(self):
            if raise_on_status:
                raise raise_on_status

    class MockClient:
        def __init__(self):
            self.method_used = None
            self.url_used = None
            self.attempts = 0

        async def request(self, method: str, url: str, **kwargs):
            self.attempts += 1
            current_exc = raise_exc_sequence.pop(0) if raise_exc_sequence else None

            if current_exc:
                raise current_exc

            self.method_used = method
            self.url_used = url
            return MockResponse()

    return AsyncHttpClient(timeout=1, retries=3, backoff=0, client=MockClient())


async def test_async_http_client():
    client = generate_mock_client([])
    cases = ["get", "post", "put", "delete", "patch"]

    for case in cases:
        # Reset attempts sequence for each case
        client._client.attempts = 0
        await getattr(client, case)("https://example.com")

        assert client._client.method_used == case.upper()
        assert client._client.url_used == "https://example.com"


@pytest.mark.parametrize("exc_class", [TimeoutException, TransportError, EOFError])
async def test_async_http_client_retries_and_succeeds(exc_class):
    # Fail the first attempt, succeed on the second
    client = generate_mock_client([exc_class("Transient error"), None])

    response = await client.get("https://example.com")

    assert response is not None
    assert client._client.attempts == int(2)
    assert client._client.method_used == "GET"


@pytest.mark.parametrize("exc_class", [TimeoutException, TransportError, EOFError])
async def test_async_http_client_exhausts_retries(exc_class):
    # Fail all attempts (retries=3 means 3 attempts total)
    client = generate_mock_client([exc_class("Persistent error")] * 3)

    with pytest.raises(HttpClientRetryError) as exc_info:
        await client.get("https://example.com")

    assert client._client.attempts == int(3)

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
async def test_async_http_client_does_not_retry_on_non_retriable_errors(exc_instance):
    # If it's an HTTPStatusError, we pass it via raise_on_status so raise_for_status()
    # triggers it
    if isinstance(exc_instance, HTTPStatusError):
        client = generate_mock_client([], raise_on_status=exc_instance)
    else:
        client = generate_mock_client([exc_instance])

    with pytest.raises(HttpClientError):
        await client.get("https://example.com")

    # Verify it failed on the very first try and did not loop/retry
    assert client._client.attempts == 1
