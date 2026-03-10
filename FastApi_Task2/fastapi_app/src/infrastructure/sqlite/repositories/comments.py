from typing import Type, Optional
from sqlalchemy.orm import Session
from src.infrastructure.sqlite.models.comments import Comment


class CommentRepository:
    def __init__(self):
        self._model: Type[Comment] = Comment

    def create(self, session: Session, comment_data: dict
    ) -> Comment:
        comment = self._model(**comment_data)
        session.add(comment)
        session.flush()
        return comment


    def get_by_id(self, session: Session, comment_id: int) -> Optional[Comment]:
        return session.query(self._model).filter(self._model.id == comment_id).first()


    def get_by_post(self, session: Session, post_id: int, skip: int = 0, limit: int = 100) -> tuple[list[Comment], int]:
        query = session.query(self._model).filter(self._model.post_id == post_id)
        total = query.count()
        comments = query.offset(skip).limit(limit).all()
        return comments, total


    def get_by_author(self, session: Session, author_id: int, skip: int = 0, limit: int = 100) -> tuple[list[Comment], int]:
        query = session.query(self._model).filter(self._model.author_id == author_id)
        total = query.count()
        comments = query.offset(skip).limit(limit).all()
        return comments, total


    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Comment], int]:
        query = session.query(self._model)
        total = query.count()
        comments = query.offset(skip).limit(limit).all()
        return comments, total


    def update(self, session: Session, comment_id: int, update_data: dict
    ) -> Optional[Comment]:
        comment = self.get_by_id(session, comment_id)
        if not comment:
            return None

        for field, value in update_data.items():
            if hasattr(comment, field) and value is not None:
                setattr(comment, field, value)

        session.flush()
        return comment


    def delete(self, session: Session, comment_id: int) -> bool:
        comment = self.get_by_id(session, comment_id)
        if not comment:
            return False
        session.delete(comment)
        session.flush()
        return True