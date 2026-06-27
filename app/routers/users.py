from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_user_repository
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()


@router.get(
    "/me",
    response_model=UserRead,
    summary="Профиль текущего пользователя",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Обновить свой профиль",
)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserRead:
    update_data = data.model_dump(exclude_unset=True)
    return await user_repo.update(current_user, update_data)
