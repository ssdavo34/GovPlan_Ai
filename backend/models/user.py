"""
사용자 모델
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """사용자 기본 모델"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """사용자 생성 모델"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """사용자 업데이트 모델"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """DB에 저장된 사용자 모델"""
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserBase):
    """사용자 응답 모델 (비밀번호 제외)"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """토큰 응답 모델"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """토큰 페이로드 모델"""
    sub: int  # user_id
    email: str
    exp: Optional[int] = None
    type: str = "access"
