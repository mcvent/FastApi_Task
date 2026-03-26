from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re

class CommentBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    author_id: int
    post_id: int

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Текст комментария не может состоять только из пробелов")
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ0-9\s\-\,\.\!\?\;\:\(\)\"\']+$", v):
            raise ValueError("Текст комментария содержит недопустимые символы")
        return v

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    text: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Текст комментария не может состоять только из пробелов")
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ0-9\s\-\,\.\!\?\;\:\(\)\"\']+$", v):
            raise ValueError("Текст комментария содержит недопустимые символы")
        return v

class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class CommentListResponse(BaseModel):
    items: List[CommentResponse]
    total: int