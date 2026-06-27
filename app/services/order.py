from decimal import Decimal

from app.core.exceptions import InsufficientStockError, InvalidOperationError, NotFoundError
from app.models.order import Order, OrderItem, OrderStatus
from app.repositories.order import OrderRepository
from app.repositories.product import ProductRepository
from app.schemas.order import OrderCreate, OrderStatusUpdate


class OrderService:
    def __init__(self, order_repo: OrderRepository, product_repo: ProductRepository):
        self.order_repo = order_repo
        self.product_repo = product_repo

    async def create_order(self, user_id: int, data: OrderCreate) -> Order:
        order_items: list[OrderItem] = []
        total = Decimal("0")

        for item in data.items:
            product = await self.product_repo.get_by_id(item.product_id)

            if product is None:
                raise NotFoundError(f"Товар с id={item.product_id} не найден")

            if not product.is_active:
                raise NotFoundError(f"Товар '{product.name}' больше не продаётся")

            if product.stock < item.quantity:
                raise InsufficientStockError(
                    f"Недостаточно товара '{product.name}' на складе: "
                    f"запрошено {item.quantity}, в наличии {product.stock}"
                )

            order_items.append(
                OrderItem(product_id=product.id, quantity=item.quantity, price=product.price)
            )
            total += product.price * item.quantity
            product.stock -= item.quantity

        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total,
            shipping_address=data.shipping_address,
            items=order_items,
        )

        self.order_repo.session.add(order)
        await self.order_repo.session.flush()
        return await self._refetch(order.id)

    async def _refetch(self, order_id: int) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        assert order is not None
        return order

    async def get_order(self, order_id: int, user_id: int | None = None) -> Order:
        order = await self.order_repo.get_by_id(order_id)

        if order is None:
            raise NotFoundError(f"Заказ {order_id} не найден")

        if user_id is not None and order.user_id != user_id:
            raise NotFoundError(f"Заказ {order_id} не найден")

        return order

    async def list_user_orders(self, user_id: int, skip: int = 0, limit: int = 100) -> tuple[list[Order], int]:
        return await self.order_repo.list_by_user(user_id, skip, limit)

    async def list_all_orders(self, skip: int = 0, limit: int = 100) -> tuple[list[Order], int]:
        items = await self.order_repo.get_all(skip, limit)
        total = await self.order_repo.count()
        return items, total

    async def update_status(self, order_id: int, data: OrderStatusUpdate) -> Order:
        order = await self.get_order(order_id)

        allowed_transitions: dict[OrderStatus, set[OrderStatus]] = {
            OrderStatus.PENDING: {OrderStatus.PAID, OrderStatus.CANCELLED},
            OrderStatus.PAID: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
            OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
            OrderStatus.DELIVERED: set(),
            OrderStatus.CANCELLED: set(),
        }

        if data.status not in allowed_transitions[order.status]:
            raise InvalidOperationError(
                f"Невозможно изменить статус заказа с '{order.status.value}' "
                f"на '{data.status.value}'"
            )

        order.status = data.status
        await self.order_repo.session.flush()
        return await self._refetch(order.id)

    async def cancel_order(self, order_id: int, user_id: int) -> Order:
        order = await self.get_order(order_id, user_id=user_id)

        if order.status not in (OrderStatus.PENDING, OrderStatus.PAID):
            raise InvalidOperationError(
                f"Невозможно отменить заказ в статусе '{order.status.value}'"
            )

        for item in order.items:
            product = await self.product_repo.get_by_id(item.product_id)
            if product is not None:
                product.stock += item.quantity

        order.status = OrderStatus.CANCELLED
        await self.order_repo.session.flush()
        return await self._refetch(order.id)
