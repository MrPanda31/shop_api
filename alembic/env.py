import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Импортируем наши настройки и Base (с метаданными всех таблиц)
from app.config import settings
from app.database import Base

# Импортируем все модели — Alembic обходит Base.metadata
# и находит таблицы только тех моделей, которые уже загружены в память.
from app.models import User, Category, Product, Order, OrderItem  # noqa: F401

# Конфиг alembic.ini
config = context.config

# Настройка логирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Передаём метаданные наших моделей — Alembic сравнивает их с БД
# и генерирует миграции автоматически (autogenerate)
target_metadata = Base.metadata

# Переопределяем URL из наших настроек (игнорируем заглушку в alembic.ini)
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """
    Offline-режим: генерирует SQL-скрипт без подключения к БД.
    Полезно для ревью миграций перед применением.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Online-режим: подключается к БД и применяет миграции.
    Используем async engine, потому что у нас asyncpg драйвер.
    """
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
