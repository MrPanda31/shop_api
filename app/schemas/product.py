from decimal import Decimal

from pydantic import Field

from app.schemas.base import AppSchema, TimestampSchema

class CategoryBase(AppSchema):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass 


class CategoryUpdate(AppSchema):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class CategoryRead(TimestampSchema, CategoryBase):
    pass


class ProductBase(AppSchema):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None

    price: Decimal = Field(gt=0, decimal_places=2)

    stock: int = Field(ge=0, default=0)
    category_id: int | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(AppSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = None
    is_active: bool | None = None


class ProductRead(TimestampSchema, ProductBase):
    is_active: bool
    category: CategoryRead | None = None


class ProductListRead(AppSchema):
    items: list[ProductRead]
    total: int
    page: int
    page_size: int
