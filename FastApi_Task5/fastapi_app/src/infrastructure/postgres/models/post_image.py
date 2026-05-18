from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.postgres.database import Base


class PostImage(Base):
    __tablename__ = "post_images"
    __table_args__ = {"schema": "application"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("application.blog_post.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(255), nullable=False)
    order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    # post = relationship("Post", back_populates="images")