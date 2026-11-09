import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.gateways.meupc_localdb.database import LocalDatabase
from infrastructure.gateways.meupc_localdb.models.storage import StorageSqlModel

EXPECTED_CAPACITY_GB = 1000
EXPECTED_PRICE_CENTS = 50000


@pytest.mark.asyncio
async def test_storage_sql_model_mapping():
    db = LocalDatabase(db_path="sqlite+aiosqlite:///:memory:")
    await db.create_all()

    async with db.get_session() as session:
        session: AsyncSession
        model_instance = StorageSqlModel(
            hash_="test_hash_123",
            slug="samsung-980-pro-1tb",
            description="Samsung 980 PRO 1TB",
            series="980 PRO",
            format_="M.2 2280",
            type_="NVMe",
            capacity_gb=EXPECTED_CAPACITY_GB,
            read=7000,
            write=5000,
            price_cents=EXPECTED_PRICE_CENTS,
            price_slip_cents=45000,
            sponsored=False,
        )
        session.add(model_instance)
        await session.commit()

        retrieved = await session.get(StorageSqlModel, "test_hash_123")
        assert retrieved is not None
        assert retrieved.slug == "samsung-980-pro-1tb"
        assert retrieved.capacity_gb == EXPECTED_CAPACITY_GB
        assert retrieved.price_cents == EXPECTED_PRICE_CENTS
        assert retrieved.sponsored is False
