from collections.abc import AsyncIterator
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from domain.entities.products import Storage
from domain.interfaces.product_repo import StorageRepo
from infrastructure.gateways.meupc_localdb.models.storage import StorageSqlModel


class LocalStorageRepo(StorageRepo):
    def __init__(self, session: AsyncSession):
        self._session = session

    def get_all(self) -> AsyncIterator[Storage]:
        async def generator():
            result = await self._session.execute(select(StorageSqlModel))
            rows = result.scalars().all()
            for row in rows:
                yield Storage(
                    hash_=row.hash_,
                    slug=row.slug,
                    description=row.description,
                    series=row.series,
                    format_=row.format_,
                    type_=row.type_,
                    capacity_gb=row.capacity_gb,
                    read=row.read,
                    write=row.write,
                    price_cents=row.price_cents,
                    price_slip_cents=row.price_slip_cents,
                    sponsored=row.sponsored,
                )

        return generator()

    async def add(self, entity: Storage) -> None:
        """Upserts a single storage entity."""
        await self.add_many([entity])

    async def add_many(self, entities: Sequence[Storage]) -> None:
        """Upserts multiple storage entities from a sequence in a single transaction."""
        for entity in entities:
            stmt = await self._session.get(StorageSqlModel, entity.hash_)
            if stmt:
                stmt.slug = entity.slug
                stmt.description = entity.description
                stmt.series = entity.series
                stmt.format_ = entity.format_
                stmt.type_ = entity.type_
                stmt.capacity_gb = entity.capacity_gb
                stmt.read = entity.read
                stmt.write = entity.write
                stmt.price_cents = entity.price_cents
                stmt.price_slip_cents = entity.price_slip_cents
                stmt.sponsored = entity.sponsored
            else:
                db_model = StorageSqlModel(
                    hash_=entity.hash_,
                    slug=entity.slug,
                    description=entity.description,
                    series=entity.series,
                    format_=entity.format_,
                    type_=entity.type_,
                    capacity_gb=entity.capacity_gb,
                    read=entity.read,
                    write=entity.write,
                    price_cents=entity.price_cents,
                    price_slip_cents=entity.price_slip_cents,
                    sponsored=entity.sponsored,
                )
                self._session.add(db_model)
        await self._session.commit()
