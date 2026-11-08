from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from domain.entities.products import Product, Storage

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    @abstractmethod
    async def get_all(self) -> list[T]:
        """Returns all entities"""
        pass

    @abstractmethod
    async def add(self, entity: T) -> None:
        """Upserts a single entity"""
        pass

    @abstractmethod
    async def add_many(self, entities: list[T]) -> None:
        """Upserts multiple entities"""
        pass


class ProductRepo(Repository[Product], ABC):
    pass


class StorageRepo(Repository[Storage], ABC):
    pass
