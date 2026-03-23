from typing import Type, Optional
from sqlalchemy.orm import Session
from src.infrastructure.sqlite.models.posts import Post


class PostRepository:
    def __init__(self):
        self._model: Type[Post] = Post

    def create(self, session: Session, post_: dict
        ) -> Post:
        post = self._model(**post_)
        session.add(post)
        session.flush()
        return post


    def get_by_id(self, session: Session, post_id: int) -> Optional[Post]:
        return session.query(self._model).filter(self._model.id == post_id).first()


    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Post], int]:
        query = session.query(self._model)
        total = query.count()
        posts = query.offset(skip).limit(limit).all()
        return posts, total


    def get_by_author(self, session: Session, author_id: int, skip: int = 0, limit: int = 100) -> tuple[list[Post], int]:
        query = session.query(self._model).filter(self._model.author_id == author_id)
        total = query.count()
        posts = query.offset(skip).limit(limit).all()
        return posts, total


    def get_published(self, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[Post], int]:
        query = session.query(self._model).filter(self._model.is_published == True)
        total = query.count()
        posts = query.offset(skip).limit(limit).all()
        return posts, total


    def update(self, session: Session, post_id: int, update_: dict
        ) -> Optional[Post]:
        post = self.get_by_id(session, post_id)
        if not post:
            return None

        for field, value in update_.items():
            if hasattr(post, field) and value is not None:
                setattr(post, field, value)

        session.flush()
        return post


    def delete(self, session: Session, post_id: int) -> bool:
        post = self.get_by_id(session, post_id)
        if not post:
            return False
        session.delete(post)
        session.flush()
        return True