from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr
from datetime import datetime
from typing import Optional, List
import re


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: Optional[str] = Field(default="", max_length=254)
    first_name: str = Field(default="", max_length=150)
    last_name: str = Field(default="", max_length=150)
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username должен содержать только буквы, цифры и подчеркивание"
            )
        if v.startswith("_") or v.endswith("_"):
            raise ValueError(
                "Username не должен начинаться или заканчиваться на подчеркивание"
            )
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v and not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s-]+$", v):
            raise ValueError(
                "Имя и фамилия должны содержать только буквы, пробелы и дефис"
            )
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(default=None, max_length=150)
    last_name: Optional[str] = Field(default=None, max_length=150)
    is_active: Optional[bool] = None
    is_staff: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v and not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s-]+$", v):
            raise ValueError(
                "Имя и фамилия должны содержать только буквы, пробелы и дефис"
            )
        return v


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_login: Optional[datetime] = None
    date_joined: datetime


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int


# Дополнительные схемы для фильтрации
class UserGetByEmailRequest(BaseModel):
    email: EmailStr


class UserGetActiveRequest(BaseModel):
    is_active: bool = True
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)