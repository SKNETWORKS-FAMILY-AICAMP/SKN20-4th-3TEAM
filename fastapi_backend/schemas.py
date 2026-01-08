from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# 사용자 관련 스키마
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


# 강아지 프로필 관련 스키마
class DogProfileCreate(BaseModel):
    name: str
    breed: Optional[str] = None
    age: Optional[int] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[str] = None
    neutered: Optional[str] = None
    health_info: Optional[str] = None
    medication: Optional[str] = None
    personality: Optional[str] = None


class DogProfileResponse(BaseModel):
    id: int
    name: str
    breed: Optional[str]
    age: Optional[int]
    birth_date: Optional[str]
    gender: Optional[str]
    size: Optional[str]
    weight: Optional[str]
    neutered: Optional[str]
    health_info: Optional[str]
    medication: Optional[str]
    personality: Optional[str]
    profile_image: Optional[str]
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 채팅 메시지 관련 스키마
class ChatMessageCreate(BaseModel):
    dog_id: int
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    dog_id: int
    message: str
    is_user: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]


# 토큰 관련 스키마
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
