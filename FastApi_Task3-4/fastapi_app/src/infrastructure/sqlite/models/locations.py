from src.infrastructure.sqlite.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Boolean, String
from datetime import datetime


class Location(Base):
    __tablename__ = "blog_location"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)