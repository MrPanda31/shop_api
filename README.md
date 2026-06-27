# Shop API

Асинхронный REST API интернет-магазина на Python. Пет-проект для изучения FastAPI, SQLAlchemy 2.0 и работы с PostgreSQL.

## Стек

- **FastAPI** — веб-фреймворк, автоматическая документация (Swagger/OpenAPI)
- **SQLAlchemy 2.0 (async)** — ORM с поддержкой async/await
- **asyncpg** — асинхронный драйвер PostgreSQL
- **Alembic** — миграции схемы БД
- **Pydantic v2** — валидация данных и схемы запросов/ответов
- **python-jose** — JWT токены
- **bcrypt** — хэширование паролей
- **PostgreSQL** — база данных

## Архитектура

Проект разделён на четыре слоя:

```
Роутеры (HTTP) → Сервисы (бизнес-логика) → Репозитории (SQL) → БД
```

- **Роутеры** (`app/routers/`) — принимают HTTP-запросы, валидируют через Pydantic-схемы, возвращают ответы
- **Сервисы** (`app/services/`) — бизнес-правила: проверка склада, расчёт суммы заказа, хэширование паролей. Не знают про HTTP
- **Репозитории** (`app/repositories/`) — SQL-запросы через SQLAlchemy. Не знают про бизнес-логику
- **Модели** (`app/models/`) — описание таблиц БД через SQLAlchemy ORM
- **Схемы** (`app/schemas/`) — Pydantic-схемы для валидации входящих данных и сериализации ответов

## Структура проекта

```
shop/
├── .env                        # переменные окружения (не коммитится)
├── .env.example                # шаблон .env
├── alembic.ini                 # конфигурация Alembic
├── requirements.txt
├── alembic/
│   ├── env.py                  # настройка миграций
│   ├── script.py.mako          # шаблон файла миграции
│   └── versions/               # сгенерированные миграции
└── app/
    ├── main.py                 # точка входа, регистрация роутеров
    ├── config.py               # настройки через pydantic-settings
    ├── database.py             # engine, сессия, get_db dependency
    ├── dependencies.py         # DI: репозитории, сервисы, авторизация, пагинация
    ├── core/
    │   ├── exceptions.py       # кастомные исключения (NotFoundError и др.)
    │   └── security.py         # хэширование паролей, JWT
    ├── models/
    │   ├── base.py             # TimestampMixin, IDMixin, AppBase
    │   ├── user.py
    │   ├── product.py          # Category, Product
    │   └── order.py            # Order, OrderItem, OrderStatus
    ├── schemas/
    │   ├── base.py             # AppSchema, TimestampSchema
    │   ├── user.py
    │   ├── product.py          # Category*, Product*, ProductListRead
    │   └── order.py            # Order*, OrderItem*, Token, CheckoutRequest
    ├── repositories/
    │   ├── base.py             # BaseRepository: get_by_id, create, update, delete
    │   ├── user.py
    │   ├── product.py          # CategoryRepository, ProductRepository
    │   └── order.py            # OrderRepository с eager loading
    ├── services/
    │   ├── auth.py             # регистрация, логин, JWT
    │   ├── product.py          # CategoryService, ProductService
    │   └── order.py            # OrderService: создание, отмена, смена статуса
    └── routers/
        ├── auth.py             # POST /register, POST /login
        ├── users.py            # GET/PATCH /me
        ├── categories.py       # CRUD категорий
        ├── products.py         # CRUD товаров + фильтрация
        └── orders.py           # заказы + смена статуса (админ)
```

## Установка и запуск

### Требования

- Python 3.12+
- PostgreSQL 14+

### Шаги

**1. Клонировать репозиторий**

```bash
git clone https://github.com/MrPanda31/shop_api.git
cd shop_api
```

**2. Создать виртуальное окружение**

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Установить зависимости**

```bash
pip install -r requirements.txt
```

**4. Настроить `.env`**

```bash
cp .env.example .env
```

Заполни `.env`:

```env
APP_NAME="Online Shop API"
APP_DEBUG=True
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/shop_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Сгенерировать `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**5. Создать базу данных**

```sql
CREATE USER shop_user WITH PASSWORD 'shop_pass';
CREATE DATABASE shop_db OWNER shop_user;
```

**6. Применить миграции**

```bash
alembic upgrade head
```

**7. Запустить сервер**

```bash
uvicorn app.main:app --reload
```

Swagger UI доступен по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)

## API

### Авторизация

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/auth/register` | Регистрация |
| POST | `/api/v1/auth/login` | Вход, получение JWT токена |

### Пользователи

| Метод | Путь | Описание | Авторизация |
|-------|------|----------|-------------|
| GET | `/api/v1/users/me` | Профиль текущего пользователя | ✅ |
| PATCH | `/api/v1/users/me` | Обновить профиль | ✅ |

### Категории

| Метод | Путь | Описание | Авторизация |
|-------|------|----------|-------------|
| GET | `/api/v1/categories` | Список категорий | — |
| GET | `/api/v1/categories/{id}` | Категория по id | — |
| POST | `/api/v1/categories` | Создать категорию | 👑 Админ |
| PATCH | `/api/v1/categories/{id}` | Обновить категорию | 👑 Админ |
| DELETE | `/api/v1/categories/{id}` | Удалить категорию | 👑 Админ |

### Товары

| Метод | Путь | Описание | Авторизация |
|-------|------|----------|-------------|
| GET | `/api/v1/products` | Каталог с фильтрами и пагинацией | — |
| GET | `/api/v1/products/{id}` | Товар по id | — |
| POST | `/api/v1/products` | Создать товар | 👑 Админ |
| PATCH | `/api/v1/products/{id}` | Обновить товар | 👑 Админ |
| DELETE | `/api/v1/products/{id}` | Удалить товар | 👑 Админ |

Query-параметры для `GET /api/v1/products`:

| Параметр | Тип | Описание |
|----------|-----|----------|
| `page` | int | Номер страницы (default: 1) |
| `page_size` | int | Размер страницы (default: 20, max: 100) |
| `category_id` | int | Фильтр по категории |
| `search` | string | Поиск по названию (регистронезависимый) |

### Заказы

| Метод | Путь | Описание | Авторизация |
|-------|------|----------|-------------|
| POST | `/api/v1/orders` | Создать заказ | ✅ |
| GET | `/api/v1/orders` | Мои заказы | ✅ |
| GET | `/api/v1/orders/{id}` | Заказ по id | ✅ |
| POST | `/api/v1/orders/{id}/cancel` | Отменить заказ | ✅ |
| GET | `/api/v1/orders/admin/all` | Все заказы | 👑 Админ |
| PATCH | `/api/v1/orders/{id}/status` | Сменить статус | 👑 Админ |

### Статусы заказа

```
pending → paid → shipped → delivered
       ↘         ↘
        cancelled  cancelled
```

## Авторизация в Swagger

1. Выполни `POST /api/v1/auth/login`
2. Скопируй `access_token` из ответа
3. Нажми кнопку **Authorize** в правом верхнем углу Swagger UI
4. Вставь токен (без слова "Bearer") и нажми Authorize

## Назначение администратора

Через psql напрямую:

```sql
UPDATE users SET is_admin = true WHERE email = 'your@email.com';
```

## Миграции

```bash
# Создать новую миграцию (autogenerate — сравнивает модели с БД)
alembic revision --autogenerate -m "описание изменений"

# Применить все новые миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# История миграций
alembic history
```
