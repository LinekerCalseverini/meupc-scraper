"""
Defines an HTTP client interface
"""

from abc import ABC, abstractmethod


class HttpClientResponse(ABC):
    cookies: dict

    @abstractmethod
    def json(self) -> dict:
        pass


class HttpClient(ABC):
    @abstractmethod
    async def request(self, method, url, **kwargs) -> HttpClientResponse:
        pass

    @abstractmethod
    async def get(self, url, **kwargs) -> HttpClientResponse:
        pass

    @abstractmethod
    async def post(self, url, **kwargs) -> HttpClientResponse:
        pass
