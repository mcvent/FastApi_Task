from pydantic import BaseModel, Field
from datetime import datetime


class Comment(BaseModel):
    text: str
    post_id: int
    author_id: int
    created_at: datetime = Field(default_factory=datetime.now, frozen=True)
