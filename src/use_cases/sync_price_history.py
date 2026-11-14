"""
This module contains the use case for syncing price history
"""

import asyncio
from typing import Generic, TypeVar
from domain.entities.products import Product
from domain.entities.dataseries import DataPoint
from domain.interfaces.product_repo import ProductRepo
from domain.interfaces.dataseries_repo import DataSeriesRepo

T = TypeVar("T", bound=Product)


class SyncPriceHistoryUseCase(Generic[T]):
    def __init__(
        self,
        product_repo: ProductRepo[T],
        source_repo: DataSeriesRepo,
        target_repo: DataSeriesRepo,
    ) -> None:
        self.product_repo = product_repo
        self.source_repo = source_repo
        self.target_repo = target_repo

    async def execute(self) -> None:
        # 1. Collect all product hashes (or tasks) first
        fetch_tasks = []
        async for product in self.product_repo.get_all():
            fetch_tasks.append(self.source_repo.get_history(product.hash_))

        # 2. Fetch all price histories concurrently (network bound)
        histories: list[list[DataPoint]] = await asyncio.gather(*fetch_tasks)

        # 3. Flatten all lists into a single collection of DataPoints
        all_data_points: list[DataPoint] = []
        for history in histories:
            all_data_points.extend(history)

        # Optional: Sort if your business logic requires chronological ordering
        all_data_points.sort(key=lambda dp: dp.date)

        # 4. Perform a single database write/transaction sequentially
        if all_data_points:
            await self.target_repo.add_history(all_data_points)
