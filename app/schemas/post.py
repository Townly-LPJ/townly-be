from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.models.post import PostCategory

# 🚨 서울(KST) 타임존 정의
KST = ZoneInfo("Asia/Seoul")

class PostCreate(BaseModel):
    category: PostCategory
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=5000)
    nickname: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=4, max_length=30)
    image_url: Optional[str] = None  # 👈 [추가] 이미지 경로 저장용

class PostUpdate(BaseModel):
    category: PostCategory
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=5000)
    password: str = Field(min_length=4, max_length=30)
    image_url: Optional[str] = None  # 👈 [추가]

class PostDelete(BaseModel):
    password: str = Field(min_length=4, max_length=30)

class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: PostCategory
    title: str
    content: str
    nickname: str
    image_url: Optional[str] = None  # 👈 [추가]
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str:
        local_dt = dt.astimezone(KST) if dt.tzinfo else dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(KST)
        return local_dt.isoformat()

class PostListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: PostCategory
    title: str
    nickname: str
    image_url: Optional[str] = None  # 👈 [추가]
    created_at: datetime

    @field_serializer("created_at")
    def serialize_datetime(self, dt: datetime) -> str:
        local_dt = dt.astimezone(KST) if dt.tzinfo else dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(KST)
        return local_dt.isoformat()