from typing import Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.infrastructure.postgres.models.posts import Post
from src.exceptions import DatabaseException, IntegrityError as DBIntegrityError


class PostRepository:
    def __init__(self):
        self._model: Type[Post] = Post

    async def create(self, session: AsyncSession, post_data: dict) -> Post:
        try:
            post = self._model(**post_data)
            session.add(post)
            await session.flush()
            return post
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных при создании поста",
                field="author_id, category_id или location_id",
                value=post_data.get("author_id")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при создании поста: {str(e)}",
                details={"table": "blog_post"}
            )

    async def get_by_id(self, session: AsyncSession, post_id: int) -> Optional[Post]:
        try:
            result = await session.execute(
                select(self._model).where(self._model.id == post_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении поста по ID: {str(e)}",
                details={"table": "blog_post", "post_id": post_id}
            )

    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> tuple[list[Post], int]:
        try:
            # Получаем общее количество
            count_result = await session.execute(select(self._model))
            total = len(count_result.scalars().all())

            # Получаем посты с пагинацией
            result = await session.execute(
                select(self._model).offset(skip).limit(limit)
            )
            posts = result.scalars().all()
            return posts, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка постов: {str(e)}",
                details={"table": "blog_post", "skip": skip, "limit": limit}
            )

    async def get_by_author(self, session: AsyncSession, author_id: int, skip: int = 0, limit: int = 100) -> tuple[
        list[Post], int]:
        try:
            # Получаем общее количество постов автора
            count_result = await session.execute(
                select(self._model).where(self._model.author_id == author_id)
            )
            total = len(count_result.scalars().all())

            # Получаем посты автора с пагинацией
            result = await session.execute(
                select(self._model)
                .where(self._model.author_id == author_id)
                .offset(skip)
                .limit(limit)
            )
            posts = result.scalars().all()
            return posts, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении постов автора: {str(e)}",
                details={"table": "blog_post", "author_id": author_id, "skip": skip, "limit": limit}
            )

    async def get_published(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> tuple[list[Post], int]:
        try:
            # Получаем общее количество опубликованных постов
            count_result = await session.execute(
                select(self._model).where(self._model.is_published == True)
            )
            total = len(count_result.scalars().all())

            # Получаем опубликованные посты с пагинацией
            result = await session.execute(
                select(self._model)
                .where(self._model.is_published == True)
                .offset(skip)
                .limit(limit)
            )
            posts = result.scalars().all()
            return posts, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении опубликованных постов: {str(e)}",
                details={"table": "blog_post", "skip": skip, "limit": limit}
            )

    async def update(self, session: AsyncSession, post_id: int, update_data: dict) -> Optional[Post]:
        try:
            # Проверяем, существует ли пост
            post = await self.get_by_id(session, post_id)
            if not post:
                return None

            # Обновляем поля
            for field, value in update_data.items():
                if hasattr(post, field) and value is not None:
                    setattr(post, field, value)

            await session.flush()
            return post
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных при обновлении поста",
                field="category_id или location_id",
                value=update_data.get("category_id") or update_data.get("location_id")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при обновлении поста: {str(e)}",
                details={"table": "blog_post", "post_id": post_id}
            )

    async def delete(self, session: AsyncSession, post_id: int) -> bool:
        try:
            result = await session.execute(
                delete(self._model).where(self._model.id == post_id)
            )
            await session.flush()
            return result.rowcount > 0
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Невозможно удалить пост (возможно, есть связанные ограничения)",
                field="post_id",
                value=post_id
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при удалении поста: {str(e)}",
                details={"table": "blog_post", "post_id": post_id}
            )