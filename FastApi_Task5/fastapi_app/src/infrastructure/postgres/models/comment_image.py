from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from src.infrastructure.postgres.database import Base


class CommentImage(Base):
    __tablename__ = "comment_images"
    __table_args__ = {"schema": "application"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(Integer, ForeignKey("application.blog_comment.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)