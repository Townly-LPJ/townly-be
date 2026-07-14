from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.post import PostCategory


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


class PostListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: PostCategory
    title: str
    nickname: str
    created_at: datetime