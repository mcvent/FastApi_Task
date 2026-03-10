from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=150)
    email: str = Field(default="", max_length=254)
    first_name: str = Field(default="", max_length=150)
    last_name: str = Field(default="", max_length=150)
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = Field(default=None, max_length=150)
    last_name: Optional[str] = Field(default=None, max_length=150)
    is_active: Optional[bool] = None
    is_staff: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_login: Optional[datetime] = None
    date_joined: datetime


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int