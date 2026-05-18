from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.infrastructure.postgres.models.comment_image import CommentImage


class CommentImageRepository:
    async def create(self, session: AsyncSession, comment_id: int, image_path: str) -> CommentImage:
        """Создать запись об изображении комментария"""
        image = CommentImage(
            comment_id=comment_id,
            image_path=image_path
        )
        session.add(image)
        await session.flush()
        return image

    async def get_by_comment(self, session: AsyncSession, comment_id: int) -> List[CommentImage]:
        """Получить все изображения комментария"""
        result = await session.execute(
            select(CommentImage).where(CommentImage.comment_id == comment_id)
        )
        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, image_id: int) -> Optional[CommentImage]:
        """Получить изображение по ID"""
        result = await session.execute(
            select(CommentImage).where(CommentImage.id == image_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, session: AsyncSession, image_id: int) -> bool:
        """Удалить запись об изображении"""
        result = await session.execute(
            delete(CommentImage).where(CommentImage.id == image_id)
        )
        return result.rowcount > 0

    async def delete_by_comment(self, session: AsyncSession, comment_id: int) -> int:
        """Удалить все изображения комментария"""
        result = await session.execute(
            delete(CommentImage).where(CommentImage.comment_id == comment_id)
        )
        return result.rowcount