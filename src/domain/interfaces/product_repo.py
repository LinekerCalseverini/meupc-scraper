from abc import ABC, abstractmethod
from typing import Generic, TypeVar, AsyncIterator, Sequence
from domain.entities.products import Product, Storage

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    @abstractmethod
    def get_all(self) -> AsyncIterator[T]:
        """Returns an async iterator of all entities"""
        pass

    @abstractmethod
    async def add(self, entity: T) -> None:
        """Upserts a single entity"""
        pass

    @abstractmethod
    async def add_many(self, entities: Sequence[T]) -> None:
        """Upserts multiple entities (accepts lists, sequences, etc.)"""
        pass


class ProductRepo(Repository[Product], ABC):
    pass


class StorageRepo(Repository[Storage], ABC):
    pass
