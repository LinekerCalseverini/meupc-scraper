from domain.entities.dataseries import DataPoint
from domain.interfaces.dataseries_repo import DataSeriesRepo
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.sqlite import insert
from infrastructure.gateways.meupc_localdb.models.price_history import (
    PriceHistorySqlModel,
)


class PriceHistoryRepo(DataSeriesRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_history(self, sku_hash: str) -> list[DataPoint]:
        return [
            DataPoint(
                sku_hash=price_history.hash_,
                date=price_history.timestamp,
                value=price_history.price_cents,
            )
            for price_history in await self.session.scalars(
                select(PriceHistorySqlModel).where(
                    PriceHistorySqlModel.hash_ == sku_hash
                )
            )
        ]

    async def add_history(self, history: list[DataPoint]) -> None:
        """
        Upserts data to the database.
        If row already exists skip that update
        """
        if not history:
            return

        values = [
            {
                "hash_": data_point.sku_hash,
                "timestamp": data_point.date,
                "price_cents": data_point.value,
            }
            for data_point in history
        ]

        stmt = insert(PriceHistorySqlModel).values(values)
        stmt = stmt.on_conflict_do_nothing()

        await self.session.execute(stmt)
        await self.session.commit()
