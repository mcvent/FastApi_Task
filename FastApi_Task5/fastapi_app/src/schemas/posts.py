from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional
import re

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    text: str = Field(..., min_length=1)
    is_published: bool = True
    author_id: int
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    image: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Заголовок не может состоять только из пробелов")
        # Разрешаем буквы (в т.ч. кириллицу), цифры, пробелы и базовую пунктуацию
        return v

class PostCreate(PostBase):
    pub_date: datetime

class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=256)
    text: Optional[str] = Field(default=None, min_length=1)
    pub_date: Optional[datetime] = None
    is_published: Optional[bool] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    image: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Заголовок не может состоять только из пробелов")
        return v

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int

class PostImageResponse(BaseModel):
    image_path: str