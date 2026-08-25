from datetime import datetime 
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password : str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    created_at: datetime


class Config:
    from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None