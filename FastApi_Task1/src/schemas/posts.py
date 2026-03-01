from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Post(BaseModel):
    title: str = Field(min_length=10, max_length=100)
    text: str
    pub_date: datetime
    author_id: int
    location_id: Optional[int] = None
    category_id: Optional[int] = None
    image: Optional[str] = None
    is_published: bool = True
