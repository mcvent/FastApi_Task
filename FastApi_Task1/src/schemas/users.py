from pydantic import BaseModel, SecretStr, Field, EmailStr


class User(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    user_id: int
    email: EmailStr
    first_name: str or None = Field(None, max_length=20)
    last_name: str or None = Field(None, max_length=20)
    password: SecretStr

