from typing import Type, Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.infrastructure.postgres.models.users import User
from src.exceptions import DatabaseException, IntegrityError as DBIntegrityError


class UserRepository:
    def __init__(self):
        self._model: Type[User] = User

    async def create(self, session: AsyncSession, user_data: dict) -> User:
        try:
            user = self._model(**user_data)
            session.add(user)
            await session.flush()
            return user
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных",
                field="username или email",
                value=user_data.get("username") or user_data.get("email")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при создании пользователя: {str(e)}",
                details={"table": "auth_user"}
            )

    async def get_by_id(self, session: AsyncSession, user_id: int) -> Optional[User]:
        try:
            result = await session.execute(
                select(self._model).where(self._model.id == user_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении пользователя: {str(e)}",
                details={"table": "auth_user", "user_id": user_id}
            )

    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        try:
            result = await session.execute(
                select(self._model).where(self._model.username == username)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении пользователя по username: {str(e)}",
                details={"table": "auth_user", "username": username}
            )

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        try:
            result = await session.execute(
                select(self._model).where(self._model.email == email)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении пользователя по email: {str(e)}",
                details={"table": "auth_user", "email": email}
            )

    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
        try:
            # Получаем общее количество
            count_result = await session.execute(
                select(func.count()).select_from(self._model)
            )
            total = count_result.scalar_one()

            # Получаем пользователей с пагинацией
            result = await session.execute(
                select(self._model).offset(skip).limit(limit)
            )
            users = result.scalars().all()
            return users, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка пользователей: {str(e)}",
                details={"table": "auth_user", "skip": skip, "limit": limit}
            )

    async def get_active_users(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
        try:
            # Получаем общее количество активных пользователей
            count_result = await session.execute(
                select(func.count()).select_from(self._model).where(self._model.is_active == True)
            )
            total = count_result.scalar_one()

            # Получаем активных пользователей с пагинацией
            result = await session.execute(
                select(self._model).where(self._model.is_active == True).offset(skip).limit(limit)
            )
            users = result.scalars().all()
            return users, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка активных пользователей: {str(e)}",
                details={"table": "auth_user", "skip": skip, "limit": limit}
            )

    async def update(self, session: AsyncSession, user_id: int, update_data: dict) -> Optional[User]:
        try:
            # Обновляем пользователя
            await session.execute(
                update(self._model)
                .where(self._model.id == user_id)
                .values(**update_data)
            )
            await session.flush()

            # Возвращаем обновлённого пользователя
            return await self.get_by_id(session, user_id)
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных при обновлении",
                field="email",
                value=update_data.get("email")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при обновлении пользователя: {str(e)}",
                details={"table": "auth_user", "user_id": user_id}
            )

    async def delete(self, session: AsyncSession, user_id: int) -> bool:
        try:
            result = await session.execute(
                delete(self._model).where(self._model.id == user_id)
            )
            await session.flush()
            return result.rowcount > 0
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Невозможно удалить пользователя (есть связанные записи)",
                field="user_id",
                value=user_id
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при удалении пользователя: {str(e)}",
                details={"table": "auth_user", "user_id": user_id}
            )

    async def username_exists(self, session: AsyncSession, username: str) -> bool:
        try:
            result = await session.execute(
                select(self._model.id).where(self._model.username == username).limit(1)
            )
            return result.first() is not None
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Данный username уже зарегистрирован: {str(e)}",
                details={"username": username}
            )

    async def email_exists(self, session: AsyncSession, email: str) -> bool:
        try:
            result = await session.execute(
                select(self._model.id).where(self._model.email == email).limit(1)
            )
            return result.first() is not None
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Данный email уже зарегистрирован: {str(e)}",
                details={"email": email}
            )