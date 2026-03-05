from pydantic import BaseModel, Field


class Category(BaseModel):
    title: str = Field(max_length=256)
    description: str
    is_published: bool = True
    slug: str = Field(
        max_length=64,
        pattern=r'^[a-zA-Z0-9_-]+$'
    )

