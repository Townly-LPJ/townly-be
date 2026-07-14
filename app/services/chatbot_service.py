from typing import Any

from app.services.tourism_search import tourism_search_service


CATEGORY_KEYWORDS = {
    "관광지": [
        "관광지",
        "관광",
        "명소",
        "볼거리",
        "갈만한 곳",
        "가볼 만한 곳",
        "가볼만한 곳",
        "데이트 장소",
        "나들이",
    ],
    "음식점": [
        "음식점",
        "식당",
        "맛집",
        "밥집",
        "먹을 곳",
        "먹거리",
        "카페",
        "커피",
        "베이커리",
        "빵집",
    ],
    "숙박": [
        "숙박",
        "숙소",
        "호텔",
        "펜션",
        "게스트하우스",
        "잘 곳",
    ],
    "축제공연행사": [
        "축제",
        "공연",
        "행사",
        "페스티벌",
        "이벤트",
    ],
    "문화시설": [
        "문화시설",
        "박물관",
        "미술관",
        "도서관",
        "전시",
        "문화",
    ],
    "레포츠": [
        "레포츠",
        "스포츠",
        "운동",
        "체험",
        "액티비티",
        "자전거",
        "캠핑",
    ],
    "쇼핑": [
        "쇼핑",
        "시장",
        "마트",
        "백화점",
        "아울렛",
        "기념품",
    ],
    "여행코스": [
        "여행코스",
        "여행 코스",
        "일정",
        "코스",
        "동선",
    ],
}


class ChatbotService:
    """지역 관광정보 챗봇 서비스."""

    def answer(
        self,
        message: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        normalized_message = message.strip()

        category = self._detect_category(normalized_message)

        search_results = tourism_search_service.search(
            query=normalized_message,
            category=category,
            limit=limit,
        )

        # 문장 전체 검색 결과가 없을 경우 검색어를 단순화해 재검색합니다.
        if not search_results:
            simplified_query = self._simplify_query(
                message=normalized_message,
                category=category,
            )

            search_results = tourism_search_service.search(
                query=simplified_query,
                category=category,
                limit=limit,
            )

        answer_text = self._create_temporary_answer(
            message=normalized_message,
            category=category,
            search_results=search_results,
        )

        return {
            "answer": answer_text,
            "places": search_results,
        }

    @staticmethod
    def _detect_category(message: str) -> str | None:
        """
        사용자 질문에서 관광 카테고리를 추론합니다.

        하나도 발견되지 않으면 None을 반환하여
        모든 카테고리를 대상으로 검색합니다.
        """

        lowered_message = message.lower()

        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in lowered_message:
                    return category

        return None

    @staticmethod
    def _simplify_query(
        message: str,
        category: str | None,
    ) -> str:
        """
        검색에 불필요한 표현을 제거합니다.

        예:
        '유성구 카페 추천해 줘'
        → '유성구 카페'
        """

        stopwords = [
            "추천해 줘",
            "추천해줘",
            "추천해 주세요",
            "추천해주세요",
            "알려 줘",
            "알려줘",
            "알려 주세요",
            "알려주세요",
            "찾아 줘",
            "찾아줘",
            "찾아 주세요",
            "찾아주세요",
            "어디 있어",
            "어디 있나요",
            "뭐가 있어",
            "뭐가 있나요",
            "갈 만한",
            "가볼 만한",
            "가볼만한",
        ]

        simplified = message.lower()

        for stopword in stopwords:
            simplified = simplified.replace(stopword, " ")

        # 카테고리 표현 자체는 주소 검색을 방해할 수 있으므로 제거합니다.
        if category:
            for keyword in CATEGORY_KEYWORDS[category]:
                simplified = simplified.replace(keyword, " ")

        simplified = " ".join(simplified.split())

        # 지역명까지 모두 제거되어 빈 문자열이 되면 원문을 사용합니다.
        return simplified or message

    @staticmethod
    def _create_temporary_answer(
        message: str,
        category: str | None,
        search_results: list[dict[str, Any]],
    ) -> str:
        """
        OpenAI 연결 전 사용할 임시 답변을 생성합니다.
        """

        if not search_results:
            return (
                f"'{message}'와 관련된 장소를 제공 데이터에서 "
                "찾지 못했습니다. 지역명이나 장소 유형을 조금 더 "
                "구체적으로 입력해 주세요."
            )

        category_text = category or "지역 정보"

        place_names = [
            place["title"]
            for place in search_results
        ]

        joined_names = ", ".join(place_names)

        return (
            f"{category_text} 관련 장소를 {len(search_results)}곳 찾았습니다. "
            f"{joined_names}입니다."
        )


chatbot_service = ChatbotService()