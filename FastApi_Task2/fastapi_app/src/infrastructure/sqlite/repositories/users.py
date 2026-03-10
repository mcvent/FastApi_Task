from typing import Type, Optional
from sqlalchemy.orm import Session
from src.infrastructure.sqlite.models.users import User


class UserRepository:
    def __init__(self):
        self._model: Type[User] = User

    def create(self, session: Session, user_data: dict) -> User:
        user = self._model(**user_data)
        session.add(user)
        session.flush()
        return user

    def get_by_id(self, session: Session, user_id: int) -> Optional[User]:
        return session.query(self._model).filter(self._model.id == user_id).first()

    def get_by_username(self, session: Session, username: str) -> Optional[User]:
        return session.query(self._model).filter(self._model.username == username).first()

    def get_by_email(self, session: Session, email: str) -> Optional[User]:
        return session.query(self._model).filter(self._model.email == email).first()

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        query = session.query(self._model)
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total

    def get_active_users(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        query = session.query(self._model).filter(self._model.is_active == True)
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total

    def update(self, session: Session, user_id: int, update_data: dict) -> Optional[User]:
        user = self.get_by_id(session, user_id)
        if not user:
            return None

        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)

        session.flush()
        return user

    def delete(self, session: Session, user_id: int) -> bool:
        user = self.get_by_id(session, user_id)
        if not user:
            return False
        session.delete(user)
        session.flush()
        return True

    def username_exists(self, session: Session, username: str) -> bool:
        return session.query(self._model).filter(self._model.username == username).first() is not None

    def email_exists(self, session: Session, email: str) -> bool:
        return session.query(self._model).filter(self._model.email == email).first() is not None