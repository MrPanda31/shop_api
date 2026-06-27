from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Приложение
    app_name: str = "Online Shop API"
    app_debug: bool = True

    # База данных
    database_url: str

    # JWT авторизация
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
