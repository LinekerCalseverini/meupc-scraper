"""
Defines a repo syncronization use case
"""

from domain.interfaces.product_repo import ProductRepo


class SyncReposUseCase:
    def __init__(self, source_repo: ProductRepo, target_repo: ProductRepo) -> None:
        """
        Constructor
        """
        self.source_repo = source_repo
        self.target_repo = target_repo

    async def execute(self):
        """
        Syncs the source repo with the target repo
        """
        products = await self.source_repo.get_all()
        await self.target_repo.add_many(products)
