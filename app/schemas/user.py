from pydantic import EmailStr, Field, field_validator

from app.schemas.base import AppSchema, TimestampSchema


class UserBase(AppSchema):
    email: EmailStr 
    username: str = Field(min_length=3, max_length=100)
    first_name: str | None = None
    last_name: str | None = None


class UserCreate(UserBase):

    password: str = Field(min_length=8, max_length=100)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not all(c.isalnum() or c == "_" for c in v):
            raise ValueError("Username может содержать только буквы, цифры и _")
        return v.lower() 


class UserUpdate(AppSchema):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = Field(default=None, min_length=3, max_length=100)


class UserRead(TimestampSchema, UserBase):
    is_active: bool
    is_admin: bool


class UserLogin(AppSchema):
    email: EmailStr
    password: str
