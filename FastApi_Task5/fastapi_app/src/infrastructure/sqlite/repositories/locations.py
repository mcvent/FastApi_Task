from typing import Type, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.infrastructure.sqlite.models.locations import Location
from src.exceptions import DatabaseException, IntegrityError as DBIntegrityError

class LocationRepository:
    def __init__(self):
        self._model: Type[Location] = Location

    def create(self, session: Session, location_data: dict) -> Location:
        try:
            location = self._model(**location_data)
            session.add(location)
            session.flush()
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

    def get_by_id(self, session: Session, location_id: int) -> Optional[Location]:
        try:
            return session.query(self._model).filter(self._model.id == location_id).first()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении локации по ID: {str(e)}",
                details={"table": "blog_location", "location_id": location_id}
            )

    def get_by_name(self, session: Session, name: str) -> Optional[Location]:
        try:
            return session.query(self._model).filter(self._model.name == name).first()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении локации по имени: {str(e)}",
                details={"table": "blog_location", "name": name}
            )

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Location], int]:
        try:
            query = session.query(self._model)
            total = query.count()
            locations = query.offset(skip).limit(limit).all()
            return locations, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении списка локаций: {str(e)}",
                details={"table": "blog_location", "skip": skip, "limit": limit}
            )

    def get_published(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Location], int]:
        try:
            query = session.query(self._model).filter(self._model.is_published == True)
            total = query.count()
            locations = query.offset(skip).limit(limit).all()
            return locations, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении опубликованных локаций: {str(e)}",
                details={"table": "blog_location", "skip": skip, "limit": limit}
            )

    def update(self, session: Session, location_id: int, update_data: dict) -> Optional[Location]:
        try:
            location = self.get_by_id(session, location_id)
            if not location:
                return None

            for field, value in update_data.items():
                if hasattr(location, field) and value is not None:
                    setattr(location, field, value)

            session.flush()
            return location
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

    def delete(self, session: Session, location_id: int) -> bool:
        try:
            location = self.get_by_id(session, location_id)
            if not location:
                return False
            session.delete(location)
            session.flush()
            return True
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

    def name_exists(self, session: Session, name: str) -> bool:
        try:
            return session.query(self._model).filter(self._model.name == name).first() is not None
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при проверке существования имени: {str(e)}",
                details={"table": "blog_location", "name": name}
            )