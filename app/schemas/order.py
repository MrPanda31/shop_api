from decimal import Decimal

from pydantic import Field

from app.models.order import OrderStatus
from app.schemas.base import AppSchema, TimestampSchema
from app.schemas.product import ProductRead


class OrderItemCreate(AppSchema):
    product_id: int
    quantity: int = Field(gt=0)


class OrderItemRead(AppSchema):
    id: int
    product_id: int
    quantity: int
    price: Decimal          # цена на момент покупки
    product: ProductRead    # вложенный объект продукта


class OrderCreate(AppSchema):
    items: list[OrderItemCreate] = Field(min_length=1)  # заказ не может быть пустым
    shipping_address: str | None = Field(default=None, max_length=500)


class OrderStatusUpdate(AppSchema):
    status: OrderStatus


class OrderRead(TimestampSchema):
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    shipping_address: str | None
    items: list[OrderItemRead]


class OrderListRead(AppSchema):
    items: list[OrderRead]
    total: int
    page: int
    page_size: int

class Token(AppSchema):
    access_token: str
    token_type: str = "bearer"


class TokenData(AppSchema):
    user_id: int
