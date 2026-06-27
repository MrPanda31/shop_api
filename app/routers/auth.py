from fastapi import APIRouter, Depends, status

from app.dependencies import get_auth_service
from app.schemas.order import Token
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register(
    data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    """
    - email должен быть валидным
    - username 3-100 символов, только буквы/цифры/_
    - password минимум 8 символов
    """
    return await auth_service.register(data)


@router.post(
    "/login",
    response_model=Token,
    summary="Вход по email и паролю",
)
async def login(
    data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    user = await auth_service.authenticate(data)
    token = auth_service.create_token(user)
    return Token(access_token=token)
