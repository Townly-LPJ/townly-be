from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+ 표준 라이브러리

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


class PostUpdate(BaseModel):
    category: PostCategory
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=5000)
    password: str = Field(min_length=4, max_length=30)


class PostDelete(BaseModel):
    password: str = Field(min_length=4, max_length=30)


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: PostCategory
    title: str
    content: str
    nickname: str
    created_at: datetime
    updated_at: datetime

    # 🚨 [추가] JSON 변환 시 UTC 시간을 한국 시간(KST) 표준 ISO 포맷으로 직렬화
    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str:
        # 데이터베이스에 저장된 UTC 시간에 타임존 정보를 주입한 뒤, KST(+09:00) 시간으로 변환합니다.
        local_dt = dt.astimezone(KST) if dt.tzinfo else dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(KST)
        return local_dt.isoformat()  # 결과 예시: "2026-07-15T10:45:46+09:00"


class PostListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: PostCategory
    title: str
    nickname: str
    created_at: datetime

    # 🚨 [추가] 목록 조회에서도 동일하게 한국 시간으로 직렬화
    @field_serializer("created_at")
    def serialize_datetime(self, dt: datetime) -> str:
        local_dt = dt.astimezone(KST) if dt.tzinfo else dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(KST)
        return local_dt.isoformat()