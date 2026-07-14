from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """이전 대화 한 건을 나타냅니다."""

    role: Literal["user", "assistant"]
    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )


class ChatRequest(BaseModel):
    """챗봇 요청 데이터입니다."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="사용자가 입력한 질문",
    )

    history: list[ChatMessage] = Field(
        default_factory=list,
        description="이전 대화 내역",
    )


class PlaceResponse(BaseModel):
    """챗봇이 찾아낸 장소 정보입니다."""

    content_id: str
    category: str
    title: str
    address: str
    telephone: str
    longitude: float | None = None
    latitude: float | None = None
    image_url: str


class ChatResponse(BaseModel):
    """챗봇 응답 데이터입니다."""

    answer: str
    places: list[PlaceResponse] = Field(default_factory=list)