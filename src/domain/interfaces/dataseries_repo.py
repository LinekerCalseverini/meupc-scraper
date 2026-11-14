"""
Defines the DataSeriesRepo interface
"""

from abc import ABC, abstractmethod

from domain.entities.dataseries import DataPoint


class DataSeriesRepo(ABC):
    @abstractmethod
    async def get_history(self, sku_hash: str) -> list[DataPoint]:
        raise NotImplementedError

    @abstractmethod
    async def add_history(self, history: list[DataPoint]) -> None:
        raise NotImplementedError
