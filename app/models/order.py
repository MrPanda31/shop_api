from decimal import Decimal
from typing import TYPE_CHECKING
import enum

from sqlalchemy import ForeignKey, Numeric, Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AppBase

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product


class OrderStatus(str, enum.Enum):
    PENDING = "pending"       # создан, ожидает оплаты
    PAID = "paid"             # оплачен
    SHIPPED = "shipped"       # передан в доставку
    DELIVERED = "delivered"   # доставлен
    CANCELLED = "cancelled"   # отменён


class Order(AppBase):
    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        default=OrderStatus.PENDING,
    )

    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    shipping_address: Mapped[str | None] = mapped_column(String(500))

    user: Mapped["User"] = relationship(
        back_populates="orders",
        lazy="selectin",
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} user_id={self.user_id} status={self.status}>"


class OrderItem(AppBase):

    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
    )

    quantity: Mapped[int] = mapped_column(Integer)

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))


    order: Mapped["Order"] = relationship(back_populates="items", lazy="selectin")
    product: Mapped["Product"] = relationship(back_populates="order_items", lazy="selectin")

    @property
    def subtotal(self) -> Decimal:
        """Сумма по этой позиции: цена × количество."""
        return self.price * self.quantity

    def __repr__(self) -> str:
        return f"<OrderItem order_id={self.order_id} product_id={self.product_id} qty={self.quantity}>"
