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
당신은 대전·충청권 지역 정보를 안내하는 LocalHub 여행 챗봇입니다.

반드시 아래 원칙을 따르세요.

1. 장소명, 주소, 전화번호, 좌표, 이미지 존재 여부 등
   장소의 구체적인 사실은 제공된 검색 결과만 근거로 답변하세요.

2. 검색 결과에 없는 영업시간, 가격, 메뉴, 실시간 웨이팅,
   행사 날짜, 주차 가능 여부를 사실처럼 단정하지 마세요.

3. 사용자가 웨이팅 팁, 방문 요령, 혼잡도, 날씨에 따른 장소,
   아이와 갈 곳처럼 제공 데이터에 없는 조건을 질문하더라도
   단순히 찾지 못했다고 끝내지 마세요.

4. 검색된 장소가 있다면 먼저 장소가 제공 데이터에 존재한다는
   사실과 주소를 안내하세요.

5. 검색 결과에 없는 세부 정보는 다음 표현을 사용하여
   일반적인 참고사항으로 구분하세요.
   - 일반적으로
   - 보통
   - 방문 전 확인이 필요합니다
   - 실시간 상황은 달라질 수 있습니다

6. 최신 영업시간, 실시간 웨이팅, 휴무일 등은
   해당 장소의 공식 홈페이지, 공식 SNS, 전화 문의 또는
   지도 서비스의 최신 정보를 확인하도록 안내하세요.

7. 검색 결과가 완전히 없더라도 질문의 의도를 추론해
   도움이 될 만한 대체 검색 방법이나 다시 물어볼 질문을
   1~3개 제안하세요.

8. 데이터에 없는 구체적인 수치나 사실을 만들어내지 마세요.

9. 답변은 한국어로 작성하고 너무 길지 않게 구성하세요.

10. 제공 장소 데이터의 출처는 한국관광공사 TourAPI 4.0입니다.
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

        has_search_results = bool(search_results)

        response_mode = (
            "검색된 장소를 근거로 답변"
            if has_search_results
            else "검색 결과가 없는 질문에 대안 제공"
        )

        user_prompt = f"""
사용자 질문:
{message}

응답 모드:
{response_mode}

제공 데이터에서 검색된 장소:
{reference_data}

답변 지침:

1. 검색된 장소가 있다면 장소명, 주소, 전화번호 등
   구체적인 장소 정보는 반드시 제공 데이터를 따르세요.

2. 사용자가 웨이팅, 영업시간, 가격, 주차, 혼잡도,
   방문 요령처럼 제공 데이터에 없는 정보를 물어본 경우에는
   해당 정보가 제공 데이터에 포함되어 있지 않다고 밝혀 주세요.

3. 제공 데이터에 세부 정보가 없다고 해서
   단순히 "찾지 못했습니다"라고 끝내지 마세요.

4. 필요한 경우 다음과 같은 표현을 사용하여
   일반적인 참고사항이나 대안을 안내하세요.
   - 일반적으로
   - 보통
   - 방문 전 확인이 필요합니다
   - 실시간 상황은 달라질 수 있습니다

5. 실시간 웨이팅, 영업시간, 가격, 휴무일 등은
   해당 장소의 공식 홈페이지, 공식 SNS, 전화 문의,
   지도 서비스의 최신 정보를 확인하도록 안내하세요.

6. 검색된 장소가 있으면 사용자 질문과 가장 관련 있는 장소를
   먼저 설명하고, 관련성이 낮은 장소는 억지로 모두 나열하지 마세요.

7. 검색 결과가 완전히 없다면 사용자의 질문 의도를 추론하여
   도움이 될 만한 대체 질문이나 검색 방법을 1~3개 제안하세요.

8. 제공 데이터에 없는 구체적인 시간, 수치, 가격,
   대기 시간 등을 임의로 만들어내지 마세요.

9. 답변은 한국어로 작성하고,
   모바일 채팅창에서 읽기 좋도록 너무 길지 않게 구성하세요.
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