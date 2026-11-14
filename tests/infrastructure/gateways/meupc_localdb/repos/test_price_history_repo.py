import pytest
from unittest.mock import AsyncMock, MagicMock
from domain.entities.dataseries import DataPoint
from infrastructure.gateways.meupc_localdb.repos.price_history_repo import (
    PriceHistoryRepo,
)

TIMESTAMP_VAL = 1000
PRICE_CENTS_VAL = 500


@pytest.mark.asyncio
async def test_local_price_history_repo_get():
    session = AsyncMock()
    session.scalars.return_value = [
        MagicMock(hash_="h1", timestamp=TIMESTAMP_VAL, price_cents=PRICE_CENTS_VAL)
    ]

    repo = PriceHistoryRepo(session=session)
    history = await repo.get_history("h1")

    assert len(history) == 1
    assert history[0].sku_hash == "h1"
    assert history[0].date == TIMESTAMP_VAL
    assert history[0].value == PRICE_CENTS_VAL


@pytest.mark.asyncio
async def test_local_price_history_repo_add():
    session = AsyncMock()
    repo = PriceHistoryRepo(session=session)

    await repo.add_history([])
    session.execute.assert_not_awaited()

    dp = DataPoint(sku_hash="h1", date=TIMESTAMP_VAL, value=PRICE_CENTS_VAL)
    await repo.add_history([dp])

    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()
