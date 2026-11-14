import pytest
from unittest.mock import AsyncMock, MagicMock
from domain.entities.products import Product
from domain.entities.dataseries import DataPoint
from use_cases.sync_price_history import SyncPriceHistoryUseCase


@pytest.mark.asyncio
async def test_sync_price_history_use_case():
    product_repo = MagicMock()

    prod = MagicMock(spec=Product)
    prod.hash_ = "test-hash"

    async def mock_get_all():
        yield prod

    product_repo.get_all = mock_get_all

    source_repo = AsyncMock()
    dp = DataPoint(sku_hash="test-hash", date=1700000000, value=1000)
    source_repo.get_history.return_value = [dp]

    target_repo = AsyncMock()

    use_case = SyncPriceHistoryUseCase(
        product_repo=product_repo,
        source_repo=source_repo,
        target_repo=target_repo,
    )

    await use_case.execute()

    source_repo.get_history.assert_awaited_once_with("test-hash")
    target_repo.add_history.assert_awaited_once_with([dp])


@pytest.mark.asyncio
async def test_sync_price_history_empty():
    product_repo = MagicMock()

    async def mock_get_all():
        if False:
            yield

    product_repo.get_all = mock_get_all

    source_repo = AsyncMock()
    target_repo = AsyncMock()

    use_case = SyncPriceHistoryUseCase(
        product_repo=product_repo,
        source_repo=source_repo,
        target_repo=target_repo,
    )

    await use_case.execute()
    target_repo.add_history.assert_not_awaited()
