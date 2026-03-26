from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re

class CategoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="", max_length=1000)
    slug: str = Field(..., min_length=1, max_length=50)
    is_published: bool = True

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Заголовок категории не может состоять только из пробелов")
        # Разрешаем буквы (в т.ч. кириллицу), цифры, пробелы и базовую пунктуацию
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ0-9\s\-\,\.\!\?]+$", v):
            raise ValueError("Заголовок содержит недопустимые символы")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Slug не может состоять только из пробелов")
        # Slug должен содержать только латиницу, цифры и дефис, без пробелов
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError("Slug должен содержать только строчные латинские буквы, цифры и дефисы (например, my-category)")
        if v.startswith('-') or v.endswith('-'):
            raise ValueError("Slug не должен начинаться или заканчиваться на дефис")
        return v

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None, max_length=1000)
    slug: Optional[str] = Field(default=None, max_length=50)
    is_published: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Заголовок категории не может состоять только из пробелов")
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ0-9\s\-\,\.\!\?]+$", v):
            raise ValueError("Заголовок содержит недопустимые символы")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Slug не может состоять только из пробелов")
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError("Slug должен содержать только строчные латинские буквы, цифры и дефисы")
        if v.startswith('-') or v.endswith('-'):
            raise ValueError("Slug не должен начинаться или заканчиваться на дефис")
        return v

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class CategoryListResponse(BaseModel):
    items: List[CategoryResponse]
    total: int