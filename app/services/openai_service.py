import asyncio
import json
from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)

from app.core.config import settings
from app.schemas.chat import ChatMessage


SYSTEM_PROMPT = """
당신은 대전·충청권 지역 정보를 안내하는 LocalHub 챗봇입니다.

반드시 아래 규칙을 따르세요.

1. 제공된 검색 결과에 있는 정보만 사실로 답변하세요.
2. 검색 결과에 없는 영업시간, 가격, 메뉴, 후기, 행사 날짜,
   주차 가능 여부 등을 추측하지 마세요.
3. 장소를 추천할 때 장소명과 주소를 함께 안내하세요.
4. 전화번호가 있는 경우에만 전화번호를 안내하세요.
5. 검색 결과가 없으면 제공 데이터에서 찾지 못했다고 말하세요.
6. 답변은 한국어로 작성하세요.
7. 답변은 읽기 쉽게 작성하되 너무 길게 설명하지 마세요.
8. 사용자의 질문과 관계없는 장소를 억지로 추천하지 마세요.
9. 좌표는 사용자가 직접 요청한 경우에만 안내하세요.
10. 제공 데이터의 출처는 한국관광공사 TourAPI 4.0입니다.
""".strip()


class OpenAIService:
    """OpenAI Responses API 호출 서비스."""

    def __init__(self) -> None:
        self.client: AsyncOpenAI | None = None

        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
            )

    def is_available(self) -> bool:
        """API 키가 설정되어 있는지 확인합니다."""

        return self.client is not None

    async def generate_answer(
        self,
        message: str,
        history: list[ChatMessage],
        search_results: list[dict[str, Any]],
    ) -> str:
        """검색 결과를 기반으로 챗봇 답변을 생성합니다."""

        if not self.client:
            raise ValueError(
                "OPENAI_API_KEY가 설정되지 않았습니다."
            )

        input_messages = self._build_input_messages(
            message=message,
            history=history,
            search_results=search_results,
        )

        try:
            response = await asyncio.wait_for(
                self.client.responses.create(
                    model=settings.OPENAI_MODEL,
                    instructions=SYSTEM_PROMPT,
                    input=input_messages,
                    max_output_tokens=500,
                ),
                timeout=20,
            )

            answer = response.output_text.strip()

            if not answer:
                raise ValueError(
                    "OpenAI 응답 내용이 비어 있습니다."
                )

            return answer

        except asyncio.TimeoutError as error:
            raise RuntimeError(
                "OpenAI 응답 시간이 초과되었습니다."
            ) from error

        except AuthenticationError as error:
            raise RuntimeError(
                "OpenAI API 키가 올바르지 않습니다."
            ) from error

        except RateLimitError as error:
            raise RuntimeError(
                "OpenAI API 사용 한도를 초과했거나 "
                "요청이 너무 많습니다."
            ) from error

        except APIConnectionError as error:
            raise RuntimeError(
                "OpenAI 서버에 연결할 수 없습니다."
            ) from error

        except APIStatusError as error:
            raise RuntimeError(
                f"OpenAI API 오류가 발생했습니다. "
                f"상태 코드: {error.status_code}"
            ) from error

    @staticmethod
    def _build_input_messages(
        message: str,
        history: list[ChatMessage],
        search_results: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        """
        이전 대화와 검색 결과를 OpenAI 입력 형태로 변환합니다.
        """

        messages: list[dict[str, str]] = []

        # 대화 기록이 지나치게 길어지는 것을 방지합니다.
        recent_history = history[-6:]

        for chat_message in recent_history:
            messages.append(
                {
                    "role": chat_message.role,
                    "content": chat_message.content,
                }
            )

        reference_data = OpenAIService._serialize_places(
            search_results,
        )

        user_prompt = f"""
사용자 질문:
{message}

제공 데이터에서 검색된 장소:
{reference_data}

위 검색 결과만 근거로 사용자 질문에 답변하세요.
검색 결과가 질문과 충분히 관련되지 않는다면,
관련 정보를 찾지 못했다고 명확히 안내하세요.
""".strip()

        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        return messages

    @staticmethod
    def _serialize_places(
        search_results: list[dict[str, Any]],
    ) -> str:
        """OpenAI에 전달할 장소 정보를 필요한 필드로 제한합니다."""

        if not search_results:
            return "검색 결과 없음"

        compact_places = []

        for place in search_results:
            compact_places.append(
                {
                    "category": place.get("category", ""),
                    "title": place.get("title", ""),
                    "address": place.get("address", ""),
                    "telephone": place.get("telephone", ""),
                    "longitude": place.get("longitude"),
                    "latitude": place.get("latitude"),
                }
            )

        return json.dumps(
            compact_places,
            ensure_ascii=False,
            indent=2,
        )


openai_service = OpenAIService()