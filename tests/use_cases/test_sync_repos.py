from use_cases.sync_repos import SyncReposUseCase
from domain.entities.products import Product
from domain.interfaces.product_repo import ProductRepo

# Create 4 products (indices 0 to 3)
skuList = [Product(f"sku_hash_{i}", f"slug_{i}") for i in range(1, 5)]


class SourceRepoMock(ProductRepo):
    def __init__(self) -> None:
        # Use a set for consistent comparison with TargetRepoMock
        self.products = set(skuList[:3])

    async def get_all(self) -> list[Product]:
        return list(self.products)

    async def add(self, product: Product) -> None:
        self.products.add(product)

    async def add_many(self, products: list[Product]) -> None:
        self.products.update(products)


class TargetRepoMock(ProductRepo):
    def __init__(self) -> None:
        self.products: set[Product] = set()

    async def get_all(self) -> list[Product]:
        return list(self.products)

    async def add(self, product: Product) -> None:
        self.products.add(product)

    async def add_many(self, products: list[Product]) -> None:
        self.products.update(products)


# Make tests async so `await` works properly
async def test_sync_repos():
    source_repo = SourceRepoMock()
    target_repo = TargetRepoMock()
    use_case = SyncReposUseCase(source_repo, target_repo)

    await use_case.execute()

    assert target_repo.products == source_repo.products


async def test_sync_repo_update():
    source_repo = SourceRepoMock()
    target_repo = TargetRepoMock()

    # Pre-populate target with one product from the list
    target_repo.products.add(skuList[1])

    use_case = SyncReposUseCase(source_repo, target_repo)
    await use_case.execute()

    assert target_repo.products == source_repo.products


async def test_sync_repo_update_without_overwrite():
    source_repo = SourceRepoMock()
    target_repo = TargetRepoMock()

    # Create an extra product that is NOT in the source repo
    target_repo.products.add(skuList[3])

    use_case = SyncReposUseCase(source_repo, target_repo)
    await use_case.execute()

    # Source repo should remain untouched with all 3 original items
    assert source_repo.products == {skuList[0], skuList[1], skuList[2]}

    # Target repo should contain the synced items PLUS the extra local item
    # (if additive)
    # Note: Depending on whether your sync is a "full overwrite/replace" or "additive",
    # adjust this assertion. Assuming add_many is additive:
    assert skuList[3] in target_repo.products
    assert target_repo.products == {
        skuList[0],
        skuList[1],
        skuList[2],
        skuList[3],
    }
