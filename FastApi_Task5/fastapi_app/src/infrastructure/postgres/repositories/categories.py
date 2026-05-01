from typing import Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.infrastructure.postgres.models.categories import Category
from src.exceptions import DatabaseException, IntegrityError as DBIntegrityError


class CategoryRepository:
    def __init__(self):
        self._model: Type[Category] = Category

    async def create(self, session: AsyncSession, category_data: dict) -> Category:
        try:
            category = self._model(**category_data)
            session.add(category)
            await session.flush()
            return category
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных при создании категории",
                field="slug",
                value=category_data.get("slug")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при создании категории: {str(e)}",
                details={"table": "blog_category"}
            )

    async def get_by_id(self, session: AsyncSession, category_id: int) -> Optional[Category]:
        try:
            result = await session.execute(
                select(self._model).where(self._model.id == category_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении категории по ID: {str(e)}",
                details={"table": "blog_category", "category_id": category_id}
            )

    async def get_by_slug(self, session: AsyncSession, slug: str) -> Optional[Category]:
        try:
            result = await session.execute(
                select(self._model).where(self._model.slug == slug)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении категории по slug: {str(e)}",
                details={"table": "blog_category", "slug": slug}
            )

    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> tuple[list[Category], int]:
        try:
            # Получаем общее количество
            count_result = await session.execute(select(self._model))
            total = len(count_result.scalars().all())

            # Получаем категории с пагинацией
            result = await session.execute(
                select(self._model).offset(skip).limit(limit)
            )
            categories = result.scalars().all()
            return list(categories), total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении списка категорий: {str(e)}",
                details={"table": "blog_category", "skip": skip, "limit": limit}
            )

    async def get_published(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> tuple[list[Category], int]:
        try:
            # Получаем общее количество опубликованных
            count_result = await session.execute(
                select(self._model).where(self._model.is_published == True)
            )
            total = len(count_result.scalars().all())

            # Получаем опубликованные категории с пагинацией
            result = await session.execute(
                select(self._model)
                .where(self._model.is_published == True)
                .offset(skip)
                .limit(limit)
            )
            categories = result.scalars().all()
            return list(categories), total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении опубликованных категорий: {str(e)}",
                details={"table": "blog_category", "skip": skip, "limit": limit}
            )

    async def update(self, session: AsyncSession, category_id: int, update_data: dict) -> Optional[Category]:
        try:
            # Проверяем существование категории
            category = await self.get_by_id(session, category_id)
            if not category:
                return None

            # Обновляем поля
            for field, value in update_data.items():
                if hasattr(category, field) and value is not None:
                    setattr(category, field, value)

            await session.flush()
            return category
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных при обновлении категории",
                field="slug",
                value=update_data.get("slug")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при обновлении категории: {str(e)}",
                details={"table": "blog_category", "category_id": category_id}
            )

    async def delete(self, session: AsyncSession, category_id: int) -> bool:
        try:
            result = await session.execute(
                delete(self._model).where(self._model.id == category_id)
            )
            await session.flush()
            return result.rowcount > 0
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Невозможно удалить категорию (возможно, есть связанные посты)",
                field="category_id",
                value=category_id
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при удалении категории: {str(e)}",
                details={"table": "blog_category", "category_id": category_id}
            )

    async def slug_exists(self, session: AsyncSession, slug: str) -> bool:
        try:
            result = await session.execute(
                select(self._model).where(self._model.slug == slug)
            )
            return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при проверке существования slug: {str(e)}",
                details={"table": "blog_category", "slug": slug}
            )