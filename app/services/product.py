from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.product import Category, Product
from app.repositories.product import CategoryRepository, ProductRepository
from app.schemas.product import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate


class CategoryService:

    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def create(self, data: CategoryCreate) -> Category:
        if await self.category_repo.get_by_name(data.name):
            raise AlreadyExistsError(f"Категория '{data.name}' уже существует")
        return await self.category_repo.create(data.model_dump())

    async def get(self, category_id: int) -> Category:
        category = await self.category_repo.get_by_id(category_id)
        if category is None:
            raise NotFoundError(f"Категория {category_id} не найдена")
        return category

    async def get_all(self) -> list[Category]:
        return await self.category_repo.get_all(limit=1000)

    async def update(self, category_id: int, data: CategoryUpdate) -> Category:
        category = await self.get(category_id)

        update_data = data.model_dump(exclude_unset=True)

        return await self.category_repo.update(category, update_data)

    async def delete(self, category_id: int) -> None:
        category = await self.get(category_id)
        await self.category_repo.delete(category)


class ProductService:
    def __init__(self, product_repo: ProductRepository, category_repo: CategoryRepository):
        self.product_repo = product_repo
        self.category_repo = category_repo

    async def create(self, data: ProductCreate) -> Product:
        if data.category_id is not None:
            category = await self.category_repo.get_by_id(data.category_id)
            if category is None:
                raise NotFoundError(f"Категория {data.category_id} не найдена")

        return await self.product_repo.create(data.model_dump())

    async def get(self, product_id: int) -> Product:
        product = await self.product_repo.get_by_id(product_id)
        if product is None:
            raise NotFoundError(f"Товар {product_id} не найден")
        return product

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
        search: str | None = None,
        only_active: bool = True,
    ) -> tuple[list[Product], int]:
        return await self.product_repo.list_with_filters(
            skip=skip,
            limit=limit,
            category_id=category_id,
            search=search,
            only_active=only_active,
        )

    async def update(self, product_id: int, data: ProductUpdate) -> Product:
        product = await self.get(product_id)
        update_data = data.model_dump(exclude_unset=True)

        new_category_id = update_data.get("category_id")
        if new_category_id is not None:
            if not await self.category_repo.get_by_id(new_category_id):
                raise NotFoundError(f"Категория {new_category_id} не найдена")

        return await self.product_repo.update(product, update_data)

    async def delete(self, product_id: int) -> None:
        product = await self.get(product_id)
        await self.product_repo.delete(product)
