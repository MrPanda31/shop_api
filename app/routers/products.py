from fastapi import APIRouter, Depends, Query, status

from app.dependencies import Pagination, get_current_admin_user, get_product_service
from app.models.user import User
from app.schemas.product import ProductCreate, ProductListRead, ProductRead, ProductUpdate
from app.services.product import ProductService

router = APIRouter()

@router.get(
    "",
    response_model=ProductListRead,
    summary="Каталог товаров с фильтрами и пагинацией",
)
async def list_products(
    pagination: Pagination = Depends(),
    category_id: int | None = Query(default=None, description="Фильтр по категории"),
    search: str | None = Query(default=None, description="Поиск по названию"),
    product_service: ProductService = Depends(get_product_service),
) -> ProductListRead:
    items, total = await product_service.list(
        skip=pagination.skip,
        limit=pagination.limit,
        category_id=category_id,
        search=search,
        only_active=True,
    )

    return ProductListRead(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Получить товар по id",
)
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
) -> ProductRead:
    return await product_service.get(product_id)

@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать товар (только админ)",
)
async def create_product(
    data: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
    admin: User = Depends(get_current_admin_user),
) -> ProductRead:
    """
    Пример тела запроса:

        {
            "name": "iPhone 15",
            "description": "128GB, черный",
            "price": "999.99",
            "stock": 50,
            "category_id": 1
        }
    """
    return await product_service.create(data)


@router.patch(
    "/{product_id}",
    response_model=ProductRead,
    summary="Обновить товар (только админ)",
)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
    admin: User = Depends(get_current_admin_user),
) -> ProductRead:
    return await product_service.update(product_id, data)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить товар (только админ)",
)
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
    admin: User = Depends(get_current_admin_user),
) -> None:

    await product_service.delete(product_id)
