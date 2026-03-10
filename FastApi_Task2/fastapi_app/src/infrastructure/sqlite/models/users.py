from src.infrastructure.sqlite.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Boolean, String
from datetime import datetime


class User(Base):
    __tablename__ = "auth_user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    last_login: Mapped[datetime or None] = mapped_column(DateTime, nullable=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(254), nullable=False, default="")
    is_staff: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    date_joined: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")