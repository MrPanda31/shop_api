from fastapi import APIRouter, Depends, status

from app.dependencies import get_category_service, get_current_admin_user
from app.models.user import User
from app.schemas.product import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.product import CategoryService

router = APIRouter()

@router.get(
    "",
    response_model=list[CategoryRead],
    summary="Список всех категорий",
)
async def list_categories(
    category_service: CategoryService = Depends(get_category_service),
) -> list[CategoryRead]:
    return await category_service.get_all()


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Получить категорию по id",
)
async def get_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryRead:
    return await category_service.get(category_id)


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать категорию (только админ)",
)
async def create_category(
    data: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
    admin: User = Depends(get_current_admin_user),
) -> CategoryRead:
    return await category_service.create(data)


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Обновить категорию (только админ)",
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    category_service: CategoryService = Depends(get_category_service),
    admin: User = Depends(get_current_admin_user),
) -> CategoryRead:
    return await category_service.update(category_id, data)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить категорию (только админ)",
)
async def delete_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    admin: User = Depends(get_current_admin_user),
) -> None:
    await category_service.delete(category_id)
