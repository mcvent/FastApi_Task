from typing import Type, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.infrastructure.sqlite.models.categories import Category
from src.exceptions import DatabaseException, IntegrityError as DBIntegrityError

class CategoryRepository:
    def __init__(self):
        self._model: Type[Category] = Category

    def create(self, session: Session, category_data: dict) -> Category:
        try:
            category = self._model(**category_data)
            session.add(category)
            session.flush()
            return category
        except IntegrityError as e:
            # Ошибка уникальности slug
            raise DBIntegrityError(
                message="Нарушение целостности данных при создании категории",
                field="slug",
                value=category_data.get("slug")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при создании категории: {str(e)}",
                details={"table": "blog_category"}
            )

    def get_by_id(self, session: Session, category_id: int) -> Optional[Category]:
        try:
            return session.query(self._model).filter(self._model.id == category_id).first()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении категории по ID: {str(e)}",
                details={"table": "blog_category", "category_id": category_id}
            )

    def get_by_slug(self, session: Session, slug: str) -> Optional[Category]:
        try:
            return session.query(self._model).filter(self._model.slug == slug).first()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении категории по slug: {str(e)}",
                details={"table": "blog_category", "slug": slug}
            )

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Category], int]:
        try:
            query = session.query(self._model)
            total = query.count()
            categories = query.offset(skip).limit(limit).all()
            return categories, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении списка категорий: {str(e)}",
                details={"table": "blog_category", "skip": skip, "limit": limit}
            )

    def get_published(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Category], int]:
        try:
            query = session.query(self._model).filter(self._model.is_published == True)
            total = query.count()
            categories = query.offset(skip).limit(limit).all()
            return categories, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении опубликованных категорий: {str(e)}",
                details={"table": "blog_category", "skip": skip, "limit": limit}
            )

    def update(self, session: Session, category_id: int, update_data: dict) -> Optional[Category]:
        try:
            category = self.get_by_id(session, category_id)
            if not category:
                return None

            for field, value in update_data.items():
                if hasattr(category, field) and value is not None:
                    setattr(category, field, value)

            session.flush()
            return category
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных при обновлении категории",
                field="slug",
                value=update_data.get("slug")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при обновлении категории: {str(e)}",
                details={"table": "blog_category", "category_id": category_id}
            )

    def delete(self, session: Session, category_id: int) -> bool:
        try:
            category = self.get_by_id(session, category_id)
            if not category:
                return False
            session.delete(category)
            session.flush()
            return True
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Невозможно удалить категорию (возможно, есть связанные посты)",
                field="category_id",
                value=category_id
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при удалении категории: {str(e)}",
                details={"table": "blog_category", "category_id": category_id}
            )

    def slug_exists(self, session: Session, slug: str) -> bool:
        try:
            return session.query(self._model).filter(self._model.slug == slug).first() is not None
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при проверке существования slug: {str(e)}",
                details={"table": "blog_category", "slug": slug}
            )