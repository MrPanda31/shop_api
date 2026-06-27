from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.repositories.base import BaseRepository

ORDER_LOAD_OPTIONS = (
    selectinload(Order.items)
    .selectinload(OrderItem.product)
    .selectinload(Product.category),
)


class OrderRepository(BaseRepository[Order]):

    model = Order

    async def get_by_id(self, id: int) -> Order | None:
        stmt = select(Order).options(*ORDER_LOAD_OPTIONS).where(Order.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Order]:
        stmt = (
            select(Order)
            .options(*ORDER_LOAD_OPTIONS)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Order], int]:
        stmt = (
            select(Order)
            .options(*ORDER_LOAD_OPTIONS)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        count_stmt = select(func.count()).select_from(Order).where(Order.user_id == user_id)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        return items, total
