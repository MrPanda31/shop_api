from app.core.exceptions import AlreadyExistsError, InvalidCredentialsError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin


class AuthService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, data: UserCreate) -> User:
        
        if await self.user_repo.get_by_email(data.email):
            raise AlreadyExistsError(f"Пользователь с email '{data.email}' уже зарегистрирован")

        if await self.user_repo.get_by_username(data.username):
            raise AlreadyExistsError(f"Username '{data.username}' уже занят")

        user_data = data.model_dump(exclude={"password"})
        user_data["hashed_password"] = hash_password(data.password)

        return await self.user_repo.create(user_data)

    async def authenticate(self, data: UserLogin) -> User:
    
        user = await self.user_repo.get_by_email(data.email)

        if user is None or not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsError("Неверный email или пароль")

        if not user.is_active:
            raise InvalidCredentialsError("Аккаунт деактивирован")

        return user

    def create_token(self, user: User) -> str:
        return create_access_token(user.id)
