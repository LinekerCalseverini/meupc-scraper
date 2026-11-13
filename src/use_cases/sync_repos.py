"""
Defines a repo synchronization use case
"""

from typing import Generic, TypeVar
from domain.interfaces.product_repo import Repository

T = TypeVar("T")


class SyncReposUseCase(Generic[T]):
    def __init__(self, source_repo: Repository[T], target_repo: Repository[T]) -> None:
        """
        Constructor
        """
        self.source_repo = source_repo
        self.target_repo = target_repo

    async def execute(self) -> None:
        """
        Syncs the source repo with the target repo in batches of 50
        """
        batch_size = 50
        batch: list[T] = []

        # Stream from the source repo (async generator)
        async for entity in self.source_repo.get_all():
            batch.append(entity)

            # When the batch reaches the target size, flush it to the target repo
            if len(batch) >= batch_size:
                await self.target_repo.add_many(batch)
                batch.clear()  # Empty the buffer for the next batch

        # Flush any remaining items that didn't fill a full batch
        if batch:
            await self.target_repo.add_many(batch)
