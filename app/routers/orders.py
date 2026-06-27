from fastapi import APIRouter, Depends, status

from app.dependencies import Pagination, get_current_admin_user, get_current_user, get_order_service
from app.models.user import User
from app.schemas.order import OrderCreate, OrderListRead, OrderRead, OrderStatusUpdate
from app.services.order import OrderService

router = APIRouter()

@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заказ",
)
async def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderRead:
    return await order_service.create_order(current_user.id, data)


@router.get(
    "",
    response_model=OrderListRead,
    summary="Мои заказы",
)
async def list_my_orders(
    pagination: Pagination = Depends(),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderListRead:
    """Список заказов текущего пользователя, новые сверху."""
    items, total = await order_service.list_user_orders(
        user_id=current_user.id,
        skip=pagination.skip,
        limit=pagination.limit,
    )
    return OrderListRead(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    summary="Получить заказ по id",
)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderRead:
    return await order_service.get_order(order_id, user_id=current_user.id)


@router.post(
    "/{order_id}/cancel",
    response_model=OrderRead,
    summary="Отменить заказ",
)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderRead:
    return await order_service.cancel_order(order_id, user_id=current_user.id)


@router.get(
    "/admin/all",
    response_model=OrderListRead,
    summary="Все заказы (только админ)",
)
async def list_all_orders(
    pagination: Pagination = Depends(),
    admin: User = Depends(get_current_admin_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderListRead:
    items, total = await order_service.list_all_orders(skip=pagination.skip, limit=pagination.limit)
    return OrderListRead(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.patch(
    "/{order_id}/status",
    response_model=OrderRead,
    summary="Изменить статус заказа (только админ)",
)
async def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    admin: User = Depends(get_current_admin_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderRead:
    """
    Пример тела запроса:
        {"status": "shipped"}

    Допустимые переходы статусов описаны в OrderService.update_status
    (ALLOWED_TRANSITIONS). Недопустимый переход → InvalidOperationError → HTTP 400
    """
    return await order_service.update_status(order_id, data)
