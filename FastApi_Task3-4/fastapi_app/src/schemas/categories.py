from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List


class CategoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="", max_length=1000)
    slug: str = Field(..., min_length=1, max_length=50)
    is_published: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None, max_length=1000)
    slug: Optional[str] = Field(default=None, max_length=50)
    is_published: Optional[bool] = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class CategoryListResponse(BaseModel):
    items: List[CategoryResponse]
    total: int