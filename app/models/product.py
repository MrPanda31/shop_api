from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import String, Text, ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AppBase

if TYPE_CHECKING:
    from app.models.order import OrderItem


class Category(AppBase):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    products: Mapped[list["Product"]] = relationship(
        back_populates="category",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name}>"


class Product(AppBase):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    stock: Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(default=True)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    category: Mapped["Category | None"] = relationship(
        back_populates="products",
        lazy="selectin",
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name} price={self.price}>"
