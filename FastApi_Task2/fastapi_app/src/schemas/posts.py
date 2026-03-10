from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    text: str = Field(..., min_length=1)
    is_published: bool = True
    author_id: int
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    image: Optional[str] = None


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


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int