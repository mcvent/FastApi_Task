from src.infrastructure.sqlite.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Boolean, String, Text
from datetime import datetime


class Category(Base):
    __tablename__ = "blog_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)