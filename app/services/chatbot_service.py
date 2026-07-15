from typing import Any

from app.schemas.chat import ChatMessage
from app.services.openai_service import openai_service
from app.services.query_analyzer import query_analyzer
from app.services.tourism_search import tourism_search_service


class ChatbotService:
    """지역 관광정보 챗봇 서비스."""

    async def answer(
        self,
        message: str,
        history: list[ChatMessage],
        limit: int = 5,
    ) -> dict[str, Any]:
        conditions = query_analyzer.analyze(
            message=message,
            history=history,
        )

        print(
            "[ChatbotService] 검색 조건:",
            {
                "category": conditions.category,
                "locations": conditions.locations,
                "detail_keywords": conditions.detail_keywords,
                "free_keywords": conditions.free_keywords,
                "require_image": conditions.require_image,
                "is_followup": conditions.is_followup,
                "search_text": conditions.search_text,
            },
        )

        search_results = tourism_search_service.search_advanced(
            query=conditions.search_text,
            category=conditions.category,
            locations=conditions.locations,
            detail_keywords=conditions.detail_keywords,
            free_keywords=conditions.free_keywords,
            require_image=conditions.require_image,
            limit=limit,
        )

        if not search_results and conditions.search_text:
            search_results = tourism_search_service.search(
                query=conditions.search_text,
                category=conditions.category,
                limit=limit,
            )

        if openai_service.is_available():
            try:
                answer_text = await openai_service.generate_answer(
                    message=conditions.original_message,
                    history=history,
                    search_results=search_results,
                )

            except RuntimeError as error:
                print(f"[OpenAI 응답 오류] {error}")

                answer_text = self._create_fallback_answer(
                    message=conditions.original_message,
                    category=conditions.category,
                    search_results=search_results,
                )

        else:
            answer_text = self._create_fallback_answer(
                message=conditions.original_message,
                category=conditions.category,
                search_results=search_results,
            )

        return {
            "answer": answer_text,
            "places": search_results,
        }

    @staticmethod
    def _create_fallback_answer(
        message: str,
        category: str | None,
        search_results: list[dict[str, Any]],
    ) -> str:
        if not search_results:
            return (
                f"'{message}'와 관련된 정보를 "
                "제공 데이터에서 찾지 못했습니다. "
                "지역명이나 장소 유형을 조금 더 "
                "구체적으로 입력해 주세요."
            )

        category_text = category or "지역 정보"
        place_descriptions = []

        for place in search_results:
            title = place["title"]
            address = place["address"]

            if address:
                place_descriptions.append(
                    f"{title}({address})"
                )
            else:
                place_descriptions.append(title)

        joined_places = ", ".join(place_descriptions)

        return (
            f"{category_text} 관련 장소를 "
            f"{len(search_results)}곳 찾았습니다. "
            f"{joined_places}입니다."
        )


chatbot_service = ChatbotService()