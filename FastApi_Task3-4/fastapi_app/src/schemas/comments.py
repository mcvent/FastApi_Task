from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List


class CommentBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    author_id: int
    post_id: int


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    text: Optional[str] = Field(default=None, max_length=1000)


class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class CommentListResponse(BaseModel):
    items: List[CommentResponse]
    total: int