from src.infrastructure.sqlite.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Text, ForeignKey, Integer
from datetime import datetime


class Comment(Base):
    __tablename__ = "blog_comment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth_user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog_post.id"), nullable=False)