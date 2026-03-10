from typing import Type, Optional
from sqlalchemy.orm import Session
from src.infrastructure.sqlite.models.categories import Category


class CategoryRepository:
    def __init__(self):
        self._model: Type[Category] = Category

    def create(self, session: Session, category_data: dict) -> Category:
        category = self._model(**category_data)
        session.add(category)
        session.flush()
        return category

    def get_by_id(self, session: Session, category_id: int) -> Optional[Category]:
        return session.query(self._model).filter(self._model.id == category_id).first()

    def get_by_slug(self, session: Session, slug: str) -> Optional[Category]:
        return session.query(self._model).filter(self._model.slug == slug).first()

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Category], int]:
        query = session.query(self._model)
        total = query.count()
        categories = query.offset(skip).limit(limit).all()
        return categories, total

    def get_published(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Category], int]:
        query = session.query(self._model).filter(self._model.is_published == True)
        total = query.count()
        categories = query.offset(skip).limit(limit).all()
        return categories, total

    def update(self, session: Session, category_id: int, update_data: dict) -> Optional[Category]:
        category = self.get_by_id(session, category_id)
        if not category:
            return None

        for field, value in update_data.items():
            if hasattr(category, field) and value is not None:
                setattr(category, field, value)

        session.flush()
        return category

    def delete(self, session: Session, category_id: int) -> bool:
        category = self.get_by_id(session, category_id)
        if not category:
            return False
        session.delete(category)
        session.flush()
        return True

    def slug_exists(self, session: Session, slug: str) -> bool:
        return session.query(self._model).filter(self._model.slug == slug).first() is not None