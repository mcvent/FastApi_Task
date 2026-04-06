from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re

class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    is_published: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Название локации не может состоять только из пробелов")
        # Разрешаем буквы (в т.ч. кириллицу), цифры, пробелы и дефис
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ0-9\s\-]+$", v):
            raise ValueError("Название локации содержит недопустимые символы")
        return v

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=256)
    is_published: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Название локации не может состоять только из пробелов")
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ0-9\s\-]+$", v):
            raise ValueError("Название локации содержит недопустимые символы")
        return v

class LocationResponse(LocationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class LocationListResponse(BaseModel):
    items: List[LocationResponse]
    total: int