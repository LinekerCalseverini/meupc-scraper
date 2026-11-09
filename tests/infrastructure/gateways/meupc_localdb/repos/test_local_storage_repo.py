import pytest
from infrastructure.gateways.meupc_localdb.database import LocalDatabase
from infrastructure.gateways.meupc_localdb.repos.storage_repo import LocalStorageRepo
from domain.entities.products import Storage

INITIAL_PRICE_CENTS = 25000
UPDATED_PRICE_CENTS = 21000


@pytest.fixture
async def local_db():
    db = LocalDatabase(db_path="sqlite+aiosqlite:///:memory:")
    await db.create_all()
    return db


@pytest.mark.asyncio
async def test_local_storage_repo_add_and_get_all(local_db):
    async with local_db.get_session() as session:
        repo = LocalStorageRepo(session)

        items = await repo.get_all()
        assert len(items) == 0

        storage_entity = Storage(
            hash_="hash_xyz",
            slug="kingston-nv2-500gb",
            description="Kingston NV2 500GB",
            series="NV2",
            format_="M.2 2280",
            type_="NVMe",
            capacity_gb=500,
            read=3000,
            write=2000,
            price_cents=INITIAL_PRICE_CENTS,
            price_slip_cents=23000,
            sponsored=True,
        )

        # Test single add contract method
        await repo.add(storage_entity)

        items = await repo.get_all()
        assert len(items) == 1
        assert items[0].hash_ == "hash_xyz"
        assert items[0].price_cents == INITIAL_PRICE_CENTS

        updated_entity = Storage(
            hash_="hash_xyz",
            slug="kingston-nv2-500gb",
            description="Kingston NV2 500GB",
            series="NV2",
            format_="M.2 2280",
            type_="NVMe",
            capacity_gb=500,
            read=3000,
            write=2000,
            price_cents=UPDATED_PRICE_CENTS,
            price_slip_cents=19000,
            sponsored=False,
        )

        # Test add_many contract method with upsert behavior
        await repo.add_many([updated_entity])

        items = await repo.get_all()
        assert len(items) == 1
        assert items[0].price_cents == UPDATED_PRICE_CENTS
        assert items[0].sponsored is False
