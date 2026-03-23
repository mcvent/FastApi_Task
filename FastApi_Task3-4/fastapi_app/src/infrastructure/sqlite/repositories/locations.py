from typing import Type, Optional
from sqlalchemy.orm import Session
from src.infrastructure.sqlite.models.locations import Location


class LocationRepository:
    def __init__(self):
        self._model: Type[Location] = Location

    def create(self, session: Session, location_: dict
    ) -> Location:
        location = self._model(**location_)
        location = self._model(**location_)
        session.add(location)
        session.flush()
        return location


    def get_by_id(self, session: Session, location_id: int) -> Optional[Location]:
        return session.query(self._model).filter(self._model.id == location_id).first()


    def get_by_name(self, session: Session, name: str) -> Optional[Location]:
        return session.query(self._model).filter(self._model.name == name).first()


    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Location], int]:
        query = session.query(self._model)
        total = query.count()
        locations = query.offset(skip).limit(limit).all()
        return locations, total


    def get_published(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Location], int]:
        query = session.query(self._model).filter(self._model.is_published == True)
        total = query.count()
        locations = query.offset(skip).limit(limit).all()
        return locations, total


    def update(self, session: Session, location_id: int, update_: dict
    ) -> Optional[Location]:
        location = self.get_by_id(session, location_id)
        if not location:
            return None

        for field, value in update_.items():
            if hasattr(location, field) and value is not None:
                setattr(location, field, value)

        session.flush()
        return location


    def delete(self, session: Session, location_id: int) -> bool:
        location = self.get_by_id(session, location_id)
        if not location:
            return False
        session.delete(location)
        session.flush()
        return True


    def name_exists(self, session: Session, name: str) -> bool:
        return session.query(self._model).filter(self._model.name == name).first() is not None