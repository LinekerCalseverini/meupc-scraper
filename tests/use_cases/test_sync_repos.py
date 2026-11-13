from collections.abc import Sequence
from use_cases.sync_repos import SyncReposUseCase
from domain.entities.products import Product
from domain.interfaces.product_repo import ProductRepo

skuList = [Product(f"sku_hash_{i}", f"slug_{i}") for i in range(1, 5)]


class SourceRepoMock(ProductRepo):
    def __init__(self) -> None:
        self.products = set(skuList[:3])

    async def get_all(self):
        for product in self.products:
            yield product

    async def add(self, entity: Product) -> None:
        self.products.add(entity)

    async def add_many(self, entities: Sequence[Product]) -> None:
        self.products.update(entities)


class TargetRepoMock(ProductRepo):
    def __init__(self) -> None:
        self.products: set[Product] = set()

    async def get_all(self):
        for product in self.products:
            yield product

    async def add(self, entity: Product) -> None:
        self.products.add(entity)

    async def add_many(self, entities: Sequence[Product]) -> None:
        self.products.update(entities)


async def test_sync_repos():
    source_repo = SourceRepoMock()
    target_repo = TargetRepoMock()
    use_case = SyncReposUseCase(source_repo, target_repo)

    await use_case.execute()

    assert target_repo.products == source_repo.products


async def test_sync_repo_update():
    source_repo = SourceRepoMock()
    target_repo = TargetRepoMock()

    target_repo.products.add(skuList[1])

    use_case = SyncReposUseCase(source_repo, target_repo)
    await use_case.execute()

    assert target_repo.products == source_repo.products


async def test_sync_repo_update_without_overwrite():
    source_repo = SourceRepoMock()
    target_repo = TargetRepoMock()

    target_repo.products.add(skuList[3])

    use_case = SyncReposUseCase(source_repo, target_repo)
    await use_case.execute()

    assert source_repo.products == {skuList[0], skuList[1], skuList[2]}
    assert skuList[3] in target_repo.products
    assert target_repo.products == {
        skuList[0],
        skuList[1],
        skuList[2],
        skuList[3],
    }
