"""
Defines a batch-throttled async HTTP client wrapper
"""

import asyncio
from infrastructure.http.async_http_client import AsyncHttpClient
from infrastructure.http.http_client import HttpClient


class RateLimitedClient(HttpClient):
    def __init__(
        self, client=None, requests_per_second: int = 10, time_window: float = 1.0
    ) -> None:
        self._client = client or AsyncHttpClient(timeout=10, retries=3)
        self._limit = requests_per_second
        self._window = time_window

        self._queue = asyncio.Queue()
        self._worker_task = None

    def _ensure_worker(self):
        """Starts the background batch worker lazily on the first request."""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._worker_loop())

    async def _worker_loop(self):
        """Background worker that processes batches of requests every time window."""
        while True:
            start_time = asyncio.get_running_loop().time()
            batch = []

            # 1. Block and wait for at least one request to process
            if self._queue.empty():
                item = await self._queue.get()
                batch.append(item)

            # 2. Grab up to the limit (e.g., 10 requests) from the queue without
            # blocking
            while len(batch) < self._limit and not self._queue.empty():
                try:
                    batch.append(self._queue.get_nowait())
                except asyncio.QueueEmpty:
                    break

            # 3. Dispatch the entire batch concurrently using asyncio.gather
            async def execute_request(item):
                method, url, kwargs, future = item
                try:
                    response = await self._client.request(method, url, **kwargs)
                    future.set_result(response)
                except Exception as e:
                    future.set_exception(e)
                finally:
                    self._queue.task_done()

            await asyncio.gather(*(execute_request(item) for item in batch))

            # 4. Enforce the time window (e.g., wait out the remainder of the 1-second
            # mark)
            elapsed = asyncio.get_running_loop().time() - start_time
            if elapsed < self._window:
                await asyncio.sleep(self._window - elapsed)

    async def request(self, method, url, **kwargs):
        """Enqueue the request and wait for the batch worker to process it."""
        self._ensure_worker()

        future = asyncio.get_running_loop().create_future()
        await self._queue.put((method, url, kwargs, future))

        return await future

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
