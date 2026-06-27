from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.product import Category, Product
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):

    model = Category

    async def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class ProductRepository(BaseRepository[Product]):

    model = Product

    async def get_by_id(self, id: int) -> Product | None:
        stmt = select(Product).options(selectinload(Product.category)).where(Product.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, obj_in: dict) -> Product:
        product = await super().create(obj_in)
        result = await self.get_by_id(product.id)
        assert result is not None 
        return result

    async def update(self, obj: Product, obj_in: dict) -> Product:
        product = await super().update(obj, obj_in)
        result = await self.get_by_id(product.id)
        assert result is not None
        return result

    async def list_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
        search: str | None = None,
        only_active: bool = True,
    ) -> tuple[list[Product], int]:

        conditions = []
        if only_active:
            conditions.append(Product.is_active == True)
        if category_id is not None:
            conditions.append(Product.category_id == category_id)
        if search:
            conditions.append(Product.name.ilike(f"%{search}%"))

        stmt = select(Product).options(selectinload(Product.category))
        for condition in conditions:
            stmt = stmt.where(condition)
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        count_stmt = select(func.count()).select_from(Product)
        for condition in conditions:
            count_stmt = count_stmt.where(condition)

        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        return items, total
