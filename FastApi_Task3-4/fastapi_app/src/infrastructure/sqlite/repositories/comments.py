from typing import Type, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.infrastructure.sqlite.models.comments import Comment
from src.exceptions import DatabaseException, IntegrityError as DBIntegrityError

class CommentRepository:
    def __init__(self):
        self._model: Type[Comment] = Comment

    def create(self, session: Session, comment_data: dict) -> Comment:
        try:
            comment = self._model(**comment_data)
            session.add(comment)
            session.flush()
            return comment
        except IntegrityError as e:
            # Ошибки FK (автор или пост не существуют)
            raise DBIntegrityError(
                message="Нарушение целостности данных при создании комментария",
                field="author_id или post_id",
                value=comment_data.get("author_id") or comment_data.get("post_id")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при создании комментария: {str(e)}",
                details={"table": "blog_comment"}
            )

    def get_by_id(self, session: Session, comment_id: int) -> Optional[Comment]:
        try:
            return session.query(self._model).filter(self._model.id == comment_id).first()
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении комментария по ID: {str(e)}",
                details={"table": "blog_comment", "comment_id": comment_id}
            )

    def get_by_post(self, session: Session, post_id: int, skip: int = 0, limit: int = 100) -> tuple[list[Comment], int]:
        try:
            query = session.query(self._model).filter(self._model.post_id == post_id)
            total = query.count()
            comments = query.offset(skip).limit(limit).all()
            return comments, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении комментариев поста: {str(e)}",
                details={"table": "blog_comment", "post_id": post_id, "skip": skip, "limit": limit}
            )

    def get_by_author(self, session: Session, author_id: int, skip: int = 0, limit: int = 100) -> tuple[list[Comment], int]:
        try:
            query = session.query(self._model).filter(self._model.author_id == author_id)
            total = query.count()
            comments = query.offset(skip).limit(limit).all()
            return comments, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении комментариев автора: {str(e)}",
                details={"table": "blog_comment", "author_id": author_id, "skip": skip, "limit": limit}
            )

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Comment], int]:
        try:
            query = session.query(self._model)
            total = query.count()
            comments = query.offset(skip).limit(limit).all()
            return comments, total
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при получении списка комментариев: {str(e)}",
                details={"table": "blog_comment", "skip": skip, "limit": limit}
            )

    def update(self, session: Session, comment_id: int, update_data: dict) -> Optional[Comment]:
        try:
            comment = self.get_by_id(session, comment_id)
            if not comment:
                return None

            for field, value in update_data.items():
                if hasattr(comment, field) and value is not None:
                    setattr(comment, field, value)

            session.flush()
            return comment
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Нарушение целостности данных при обновлении комментария",
                field="post_id или author_id",
                value=update_data.get("post_id") or update_data.get("author_id")
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при обновлении комментария: {str(e)}",
                details={"table": "blog_comment", "comment_id": comment_id}
            )

    def delete(self, session: Session, comment_id: int) -> bool:
        try:
            comment = self.get_by_id(session, comment_id)
            if not comment:
                return False
            session.delete(comment)
            session.flush()
            return True
        except IntegrityError as e:
            raise DBIntegrityError(
                message="Невозможно удалить комментарий (возможно, есть связанные ограничения)",
                field="comment_id",
                value=comment_id
            )
        except SQLAlchemyError as e:
            raise DatabaseException(
                message=f"Ошибка БД при удалении комментария: {str(e)}",
                details={"table": "blog_comment", "comment_id": comment_id}
            )