from typing import Type, Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.infrastructure.postgres.models.comments import Comment
from src.exceptions import DatabaseException, IntegrityError as DBIntegrityError


class CommentRepository:
    def __init__(self):
        self._model: Type[Comment] = Comment

    async def create(self, session: AsyncSession, comment_data: dict) -> Comment:
        try:
            comment = self._model(**comment_data)
            session.add(comment)
            await session.flush()
            return comment
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных при создании комментария",
                field="author_id или post_id",
                value=comment_data.get("author_id") or comment_data.get("post_id")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при создании комментария: {str(e)}",
                details={"table": "blog_comment"}
            )

    async def get_by_id(self, session: AsyncSession, comment_id: int) -> Optional[Comment]:
        try:
            result = await session.execute(
                select(self._model).where(self._model.id == comment_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении комментария по ID: {str(e)}",
                details={"table": "blog_comment", "comment_id": comment_id}
            )

    async def get_by_post(self, session: AsyncSession, post_id: int, skip: int = 0, limit: int = 100) -> Tuple[
        List[Comment], int]:
        try:
            # Считаем общее количество
            count_result = await session.execute(
                select(self._model).where(self._model.post_id == post_id)
            )
            total = len(count_result.scalars().all())

            # Получаем комментарии с пагинацией
            result = await session.execute(
                select(self._model)
                .where(self._model.post_id == post_id)
                .offset(skip)
                .limit(limit)
            )
            comments = result.scalars().all()
            return comments, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении комментариев поста: {str(e)}",
                details={"table": "blog_comment", "post_id": post_id, "skip": skip, "limit": limit}
            )

    async def get_by_author(self, session: AsyncSession, author_id: int, skip: int = 0, limit: int = 100) -> Tuple[
        List[Comment], int]:
        try:
            # Считаем общее количество
            count_result = await session.execute(
                select(self._model).where(self._model.author_id == author_id)
            )
            total = len(count_result.scalars().all())

            # Получаем комментарии с пагинацией
            result = await session.execute(
                select(self._model)
                .where(self._model.author_id == author_id)
                .offset(skip)
                .limit(limit)
            )
            comments = result.scalars().all()
            return comments, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении комментариев автора: {str(e)}",
                details={"table": "blog_comment", "author_id": author_id, "skip": skip, "limit": limit}
            )

    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> Tuple[List[Comment], int]:
        try:
            # Считаем общее количество
            count_result = await session.execute(select(self._model))
            total = len(count_result.scalars().all())

            # Получаем комментарии с пагинацией
            result = await session.execute(
                select(self._model).offset(skip).limit(limit)
            )
            comments = result.scalars().all()
            return comments, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении списка комментариев: {str(e)}",
                details={"table": "blog_comment", "skip": skip, "limit": limit}
            )

    async def update(self, session: AsyncSession, comment_id: int, update_data: dict) -> Optional[Comment]:
        try:
            await session.execute(
                update(self._model)
                .where(self._model.id == comment_id)
                .values(**update_data)
            )
            await session.flush()

            # Возвращаем обновлённый комментарий
            return await self.get_by_id(session, comment_id)
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных при обновлении комментария",
                field="post_id или author_id",
                value=update_data.get("post_id") or update_data.get("author_id")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при обновлении комментария: {str(e)}",
                details={"table": "blog_comment", "comment_id": comment_id}
            )

    async def delete(self, session: AsyncSession, comment_id: int) -> bool:
        try:
            result = await session.execute(
                delete(self._model).where(self._model.id == comment_id)
            )
            await session.flush()
            return result.rowcount > 0
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Невозможно удалить комментарий (возможно, есть связанные ограничения)",
                field="comment_id",
                value=comment_id
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при удалении комментария: {str(e)}",
                details={"table": "blog_comment", "comment_id": comment_id}
            )

    async def delete_by_post_id(self, session: AsyncSession, post_id: int) -> int:
        """Удаляет все комментарии поста. Возвращает количество удаленных комментариев."""
        try:
            # Получаем все комментарии поста
            result = await session.execute(
                select(self._model).where(self._model.post_id == post_id)
            )
            comments = result.scalars().all()
            count = len(comments)

            # Удаляем каждый комментарий
            for comment in comments:
                await session.delete(comment)

            await session.flush()
            return count
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при удалении комментариев поста: {str(e)}",
                details={"table": "blog_comment", "post_id": post_id}
            )