"""
Defines an HTTP client interface
"""

from abc import ABC, abstractmethod


class HttpClient(ABC):
    @abstractmethod
    async def request(self, method, url, **kwargs):
        pass

    @abstractmethod
    async def get(self, url, **kwargs):
        pass

    @abstractmethod
    async def post(self, url, **kwargs):
        pass
