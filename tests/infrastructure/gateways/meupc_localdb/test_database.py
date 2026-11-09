import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.gateways.meupc_localdb.database import LocalDatabase, Base


@pytest.mark.asyncio
async def test_local_database_initialization():
    db = LocalDatabase(db_path="sqlite+aiosqlite:///:memory:")

    assert db.engine is not None
    assert db.async_session_maker is not None

    session = db.get_session()
    assert isinstance(session, AsyncSession)
    await session.close()


@pytest.mark.asyncio
async def test_local_database_create_all():
    db = LocalDatabase(db_path="sqlite+aiosqlite:///:memory:")
    await db.create_all()

    async with db.engine.begin() as conn:

        def check_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        tables = await conn.run_sync(check_tables)
        assert "storages" in tables

    assert "storages" in Base.metadata.tables
