from typing import Type, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.infrastructure.sqlite.models.posts import Post
from src.exceptions import DatabaseException, IntegrityError as DBIntegrityError

class PostRepository:
    def __init__(self):
        self._model: Type[Post] = Post

    def create(self, session: Session, post_data: dict) -> Post:
        try:
            post = self._model(**post_data)
            session.add(post)
            session.flush()
            return post
        except IntegrityError as e:
            # Например, если есть уникальные ограничения или проблемы с FK
            raise DBIntegrityError(
                message="Нарушение целостности данных при создании поста",
                field="author_id, category_id или location_id",
                value=post_data.get("author_id")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при создании поста: {str(e)}",
                details={"table": "blog_post"}
            )

    def get_by_id(self, session: Session, post_id: int) -> Optional[Post]:
        try:
            return session.query(self._model).filter(self._model.id == post_id).first()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении поста по ID: {str(e)}",
                details={"table": "blog_post", "post_id": post_id}
            )

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Post], int]:
        try:
            query = session.query(self._model)
            total = query.count()
            posts = query.offset(skip).limit(limit).all()
            return posts, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка постов: {str(e)}",
                details={"table": "blog_post", "skip": skip, "limit": limit}
            )

    def get_by_author(self, session: Session, author_id: int, skip: int = 0, limit: int = 100) -> tuple[list[Post], int]:
        try:
            query = session.query(self._model).filter(self._model.author_id == author_id)
            total = query.count()
            posts = query.offset(skip).limit(limit).all()
            return posts, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении постов автора: {str(e)}",
                details={"table": "blog_post", "author_id": author_id, "skip": skip, "limit": limit}
            )

    def get_published(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Post], int]:
        try:
            query = session.query(self._model).filter(self._model.is_published == True)
            total = query.count()
            posts = query.offset(skip).limit(limit).all()
            return posts, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при получении опубликованных постов: {str(e)}",
                details={"table": "blog_post", "skip": skip, "limit": limit}
            )

    def update(self, session: Session, post_id: int, update_data: dict) -> Optional[Post]:
        try:
            post = self.get_by_id(session, post_id)
            if not post:
                return None

            for field, value in update_data.items():
                if hasattr(post, field) and value is not None:
                    setattr(post, field, value)

            session.flush()
            return post
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных при обновлении поста",
                field="category_id или location_id",
                value=update_data.get("category_id") or update_data.get("location_id")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при обновлении поста: {str(e)}",
                details={"table": "blog_post", "post_id": post_id}
            )

    def delete(self, session: Session, post_id: int) -> bool:
        try:
            post = self.get_by_id(session, post_id)
            if not post:
                return False
            session.delete(post)
            session.flush()
            return True
        except IntegrityError as e:
            # Например, если есть каскадные ограничения или связанные записи, которые нельзя удалить
            raise DBIntegrityError(
                message="Невозможно удалить пост (возможно, есть связанные ограничения)",
                field="post_id",
                value=post_id
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка при удалении поста: {str(e)}",
                details={"table": "blog_post", "post_id": post_id}
            )