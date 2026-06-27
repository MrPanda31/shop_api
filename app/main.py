from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import (
    AlreadyExistsError,
    AppException,
    InsufficientStockError,
    InvalidCredentialsError,
    InvalidOperationError,
    NotFoundError,
    PermissionDeniedError,
)
from app.routers import auth, categories, orders, products, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"-------------Starting {settings.app_name}----------------")
    yield
    print("--------------Shutting down...------------")

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="REST API интернет-магазина",
    lifespan=lifespan,
)


EXCEPTION_STATUS_MAP: dict[type[AppException], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    AlreadyExistsError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    PermissionDeniedError: status.HTTP_403_FORBIDDEN,
    InsufficientStockError: status.HTTP_400_BAD_REQUEST,
    InvalidOperationError: status.HTTP_400_BAD_REQUEST,
}


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    status_code = EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "app": settings.app_name}

#routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
