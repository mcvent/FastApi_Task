from typing import Type, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from src.infrastructure.sqlite.models.users import User
from src.exceptions import DatabaseException, IntegrityError as DBIntegrityError

class UserRepository:
    def __init__(self):
        self._model: Type[User] = User

    def create(self, session: Session, user_data: dict) -> User:
        try:
            user = self._model(**user_data)
            session.add(user)
            session.flush()
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

    def get_by_id(self, session: Session, user_id: int) -> Optional[User]:
        try:
            return session.query(self._model).filter(self._model.id == user_id).first()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении пользователя: {str(e)}",
                details={"table": "auth_user", "user_id": user_id}
            )

    def get_by_username(self, session: Session, username: str) -> Optional[User]:
        try:
            return session.query(self._model).filter(self._model.username == username).first()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении пользователя по username: {str(e)}",
                details={"table": "auth_user", "username": username}
            )

    def get_by_email(self, session: Session, email: str) -> Optional[User]:
        try:
            return session.query(self._model).filter(self._model.email == email).first()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении пользователя по email: {str(e)}",
                details={"table": "auth_user", "email": email}
            )

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        try:
            query = session.query(self._model)
            total = query.count()
            users = query.offset(skip).limit(limit).all()
            return users, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка пользователей: {str(e)}",
                details={"table": "auth_user", "skip": skip, "limit": limit}
            )

    def get_active_users(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        try:
            query = session.query(self._model).filter(self._model.is_active == True)
            total = query.count()
            users = query.offset(skip).limit(limit).all()
            return users, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка активных пользователей: {str(e)}",
                details={"table": "auth_user", "skip": skip, "limit": limit}
            )


    def update(self, session: Session, user_id: int, update_data: dict) -> Optional[User]:
        try:
            user = self.get_by_id(session, user_id)
            if not user:
                return None

            for field, value in update_data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)

            session.flush()
            return user
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

    def delete(self, session: Session, user_id: int) -> bool:
        try:
            user = self.get_by_id(session, user_id)
            if not user:
                return False
            session.delete(user)
            session.flush()
            return True
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

    def username_exists(self, session: Session, username: str) -> bool:
        try:
            return session.query(self._model).filter(self._model.username == username).first() is not None
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Данный username уже зарегистрирован: {str(e)}",
                details={"username": username}
            )

    def email_exists(self, session: Session, email: str) -> bool:
        try:
            return session.query(self._model).filter(self._model.email == email).first() is not None
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Данный email уже зарегистрирован: {str(e)}",
                details={"email": email}
            )