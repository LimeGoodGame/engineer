from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    confirm_password: str
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('password must be at least 8 characters')
        if len(v) > 128:
            raise ValueError('password must be less than 128 characters')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str

    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('password must be at least 8 characters')
        if len(v) > 128:
            raise ValueError('password must be less than 128 characters')
        return v