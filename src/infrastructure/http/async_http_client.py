"""

Defines an async HTTP client

"""

import asyncio
import httpx
from httpx import AsyncClient, TimeoutException, TransportError

from infrastructure.http.http_client import HttpClient
from infrastructure.http.errors import (
    HttpClientRetryError,
    HttpClientTimeoutError,
    HttpClientError,
)


class AsyncHttpClient(HttpClient):
    def __init__(
        self, timeout: int, retries: int, client=None, backoff: int = 1
    ) -> None:
        self.timeout = timeout
        self.retries = retries
        self._backoff = backoff
        self._client = client or AsyncClient()

    async def request(self, method, url, **kwargs):
        last_exception = None
        backoff = self._backoff

        for attempt in range(self.retries):
            try:
                response = await self._client.request(
                    method, url, timeout=self.timeout, **kwargs
                )

                # Optional: Uncomment if you want to raise status errors immediately
                # (without retrying 4xx/5xx)
                response.raise_for_status()

                return response

            except TimeoutException:
                last_exception = HttpClientTimeoutError(self.timeout)

            except (TransportError, EOFError) as e:
                last_exception = e

            except httpx.HTTPStatusError as e:
                # Let HTTP status errors (4xx, 5xx) bubble up immediately with their
                # original context
                raise HttpClientError(
                    f"HTTP status error: {e.response.status_code}"
                ) from e

            except Exception as e:
                # Truly unexpected programming or configuration bugs
                raise HttpClientError("Unexpected error occurred") from e

            # If we reached here, an eligible retry error occurred. Wait before next
            # attempt.
            await asyncio.sleep(backoff)
            backoff *= 2  # Exponential backoff for the *next* retry

        # If all retries are exhausted
        raise HttpClientRetryError(self.retries) from last_exception

    async def get(self, url, **kwargs):
        return await self.request("GET", url, **kwargs)

    async def post(self, url, **kwargs):
        return await self.request("POST", url, **kwargs)

    async def put(self, url, **kwargs):
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url, **kwargs):
        return await self.request("DELETE", url, **kwargs)

    async def patch(self, url, **kwargs):
        return await self.request("PATCH", url, **kwargs)
