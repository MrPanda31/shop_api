from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User
from app.repositories.order import OrderRepository
from app.repositories.product import CategoryRepository, ProductRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.order import OrderService
from app.services.product import CategoryService, ProductService

# =============================================================================
# РЕПОЗИТОРИИ
# =============================================================================

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_category_repository(db: AsyncSession = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)


def get_product_repository(db: AsyncSession = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)


def get_order_repository(db: AsyncSession = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)


# =============================================================================
# СЕРВИСЫ
# =============================================================================

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)


def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    return CategoryService(category_repo)


def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    category_repo: CategoryRepository = Depends(get_category_repository),
) -> ProductService:
    return ProductService(product_repo, category_repo)


def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> OrderService:
    return OrderService(order_repo, product_repo)


# =============================================================================
# АВТОРИЗАЦИЯ
# =============================================================================

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:

    token = credentials.credentials
    user_id = decode_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_by_id(user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или деактивирован",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )
    return current_user


# =============================================================================
# ПАГИНАЦИЯ
# =============================================================================


class Pagination:
    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Номер страницы, начиная с 1"),
        page_size: int = Query(default=20, ge=1, le=100, description="Размер страницы"),
    ):
        self.page = page
        self.page_size = page_size

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size
