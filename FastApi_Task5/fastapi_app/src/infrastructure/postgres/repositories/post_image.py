from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from src.infrastructure.postgres.models.post_image import PostImage


class PostImageRepository:
    async def create(self, session: AsyncSession, post_id: int, image_path: str, order: int = 0) -> PostImage:
        """Создать запись об изображении поста"""
        image = PostImage(
            post_id=post_id,
            image_path=image_path,
            order=order
        )
        session.add(image)
        await session.flush()
        return image

    async def get_by_post(self, session: AsyncSession, post_id: int) -> List[PostImage]:
        """Получить все изображения поста (сортировка по order)"""
        result = await session.execute(
            select(PostImage)
            .where(PostImage.post_id == post_id)
            .order_by(PostImage.order)
        )
        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, image_id: int) -> Optional[PostImage]:
        """Получить изображение по ID"""
        result = await session.execute(
            select(PostImage).where(PostImage.id == image_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, session: AsyncSession, image_id: int) -> bool:
        """Удалить запись об изображении"""
        result = await session.execute(
            delete(PostImage).where(PostImage.id == image_id)
        )
        return result.rowcount > 0

    async def delete_by_post(self, session: AsyncSession, post_id: int) -> int:
        """Удалить все изображения поста"""
        result = await session.execute(
            delete(PostImage).where(PostImage.post_id == post_id)
        )
        return result.rowcount

    async def update_order(self, session: AsyncSession, image_id: int, new_order: int) -> None:
        """Обновить порядок изображения"""
        await session.execute(
            update(PostImage)
            .where(PostImage.id == image_id)
            .values(order=new_order)
        )