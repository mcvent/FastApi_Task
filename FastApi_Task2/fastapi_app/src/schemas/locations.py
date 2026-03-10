from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List


class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    is_published: bool = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=256)
    is_published: Optional[bool] = None


class LocationResponse(LocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class LocationListResponse(BaseModel):
    items: List[LocationResponse]
    total: int