from typing import Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.infrastructure.postgres.models.locations import Location
from src.exceptions import DatabaseException, IntegrityError as DBIntegrityError


class LocationRepository:
    def __init__(self):
        self._model: Type[Location] = Location

    async def create(self, session: AsyncSession, location_data: dict) -> Location:
        try:
            location = self._model(**location_data)
            session.add(location)
            await session.flush()
            await session.refresh(location)
            return location
        except IntegrityError as e:
            # Ошибка уникальности имени
            raise DBIntegrityError(
                message="Нарушение целостности данных: локация с таким именем уже существует",
                field="name",
                value=location_data.get("name")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при создании локации: {str(e)}",
                details={"table": "blog_location"}
            )

    async def get_by_id(self, session: AsyncSession, location_id: int) -> Optional[Location]:
        try:
            result = await session.execute(
                select(self._model).where(self._model.id == location_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении локации по ID: {str(e)}",
                details={"table": "blog_location", "location_id": location_id}
            )

    async def get_by_name(self, session: AsyncSession, name: str) -> Optional[Location]:
        try:
            result = await session.execute(
                select(self._model).where(self._model.name == name)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении локации по имени: {str(e)}",
                details={"table": "blog_location", "name": name}
            )

    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> tuple[list[Location], int]:
        try:
            # Получаем общее количество
            count_result = await session.execute(select(func.count()).select_from(self._model))
            total = count_result.scalar_one()

            # Получаем записи с пагинацией
            result = await session.execute(
                select(self._model).offset(skip).limit(limit)
            )
            locations = result.scalars().all()
            return locations, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении списка локаций: {str(e)}",
                details={"table": "blog_location", "skip": skip, "limit": limit}
            )

    async def get_published(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> tuple[list[Location], int]:
        try:
            # Получаем общее количество опубликованных
            count_result = await session.execute(
                select(func.count()).where(self._model.is_published == True)
            )
            total = count_result.scalar_one()

            # Получаем опубликованные записи с пагинацией
            result = await session.execute(
                select(self._model).where(self._model.is_published == True).offset(skip).limit(limit)
            )
            locations = result.scalars().all()
            return locations, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении опубликованных локаций: {str(e)}",
                details={"table": "blog_location", "skip": skip, "limit": limit}
            )

    async def update(self, session: AsyncSession, location_id: int, update_data: dict) -> Optional[Location]:
        try:
            # Сначала проверяем, существует ли запись
            existing = await self.get_by_id(session, location_id)
            if not existing:
                return None

            # Выполняем обновление
            await session.execute(
                update(self._model)
                .where(self._model.id == location_id)
                .values(**update_data)
            )
            await session.flush()

            # Возвращаем обновлённую запись
            return await self.get_by_id(session, location_id)
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных: локация с таким именем уже существует",
                field="name",
                value=update_data.get("name")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при обновлении локации: {str(e)}",
                details={"table": "blog_location", "location_id": location_id}
            )

    async def delete(self, session: AsyncSession, location_id: int) -> bool:
        try:
            result = await session.execute(
                delete(self._model).where(self._model.id == location_id)
            )
            await session.flush()
            return result.rowcount > 0
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Невозможно удалить локацию (возможно, есть связанные посты)",
                field="location_id",
                value=location_id
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при удалении локации: {str(e)}",
                details={"table": "blog_location", "location_id": location_id}
            )

    async def name_exists(self, session: AsyncSession, name: str) -> bool:
        try:
            result = await session.execute(
                select(self._model).where(self._model.name == name)
            )
            return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при проверке существования имени: {str(e)}",
                details={"table": "blog_location", "name": name}
            )