# from typing import Any

# from app.schemas.chat import ChatMessage
# from app.services.openai_service import openai_service
# from app.services.tourism_search import tourism_search_service


# CATEGORY_KEYWORDS = {
#     "관광지": [
#         "관광지",
#         "관광",
#         "명소",
#         "볼거리",
#         "갈만한 곳",
#         "가볼 만한 곳",
#         "가볼만한 곳",
#         "데이트 장소",
#         "나들이",
#     ],
#     "음식점": [
#         "음식점",
#         "식당",
#         "맛집",
#         "밥집",
#         "먹을 곳",
#         "먹거리",
#         "카페",
#         "커피",
#         "베이커리",
#         "빵집",
#     ],
#     "숙박": [
#         "숙박",
#         "숙소",
#         "호텔",
#         "펜션",
#         "게스트하우스",
#         "잘 곳",
#     ],
#     "축제공연행사": [
#         "축제",
#         "공연",
#         "행사",
#         "페스티벌",
#         "이벤트",
#     ],
#     "문화시설": [
#         "문화시설",
#         "박물관",
#         "미술관",
#         "도서관",
#         "전시",
#         "문화",
#     ],
#     "레포츠": [
#         "레포츠",
#         "스포츠",
#         "운동",
#         "체험",
#         "액티비티",
#         "자전거",
#         "캠핑",
#     ],
#     "쇼핑": [
#         "쇼핑",
#         "시장",
#         "마트",
#         "백화점",
#         "아울렛",
#         "기념품",
#     ],
#     "여행코스": [
#         "여행코스",
#         "여행 코스",
#         "일정",
#         "코스",
#         "동선",
#     ],
# }


# class ChatbotService:
#     """지역 관광정보 챗봇 서비스."""

#     async def answer(
#         self,
#         message: str,
#         history: list[ChatMessage],
#         limit: int = 5,
#     ) -> dict[str, Any]:
#         normalized_message = message.strip()

#         category = self._detect_category(
#             normalized_message
#         )

#         search_results = tourism_search_service.search(
#             query=normalized_message,
#             category=category,
#             limit=limit,
#         )

#         if not search_results:
#             simplified_query = self._simplify_query(
#                 message=normalized_message,
#                 category=category,
#             )

#             search_results = tourism_search_service.search(
#                 query=simplified_query,
#                 category=category,
#                 limit=limit,
#             )

#         # OpenAI API가 정상 설정된 경우 자연어 답변 생성
#         if openai_service.is_available():
#             try:
#                 answer_text = await openai_service.generate_answer(
#                     message=normalized_message,
#                     history=history,
#                     search_results=search_results,
#                 )

#             except RuntimeError as error:
#                 print(f"[OpenAI 응답 오류] {error}")

#                 # 외부 API 장애 시에도 챗봇 전체가 실패하지 않도록
#                 # 임시 답변으로 대체합니다.
#                 answer_text = self._create_fallback_answer(
#                     message=normalized_message,
#                     category=category,
#                     search_results=search_results,
#                 )

#         else:
#             print(
#                 "[경고] OPENAI_API_KEY가 없어 "
#                 "기본 답변을 반환합니다."
#             )

#             answer_text = self._create_fallback_answer(
#                 message=normalized_message,
#                 category=category,
#                 search_results=search_results,
#             )

#         return {
#             "answer": answer_text,
#             "places": search_results,
#         }

#     @staticmethod
#     def _detect_category(
#         message: str,
#     ) -> str | None:
#         lowered_message = message.lower()

#         for category, keywords in CATEGORY_KEYWORDS.items():
#             for keyword in keywords:
#                 if keyword in lowered_message:
#                     return category

#         return None

#     @staticmethod
#     def _simplify_query(
#         message: str,
#         category: str | None,
#     ) -> str:
#         stopwords = [
#             "추천해 줘",
#             "추천해줘",
#             "추천해 주세요",
#             "추천해주세요",
#             "알려 줘",
#             "알려줘",
#             "알려 주세요",
#             "알려주세요",
#             "찾아 줘",
#             "찾아줘",
#             "찾아 주세요",
#             "찾아주세요",
#             "어디 있어",
#             "어디 있나요",
#             "뭐가 있어",
#             "뭐가 있나요",
#             "갈 만한",
#             "가볼 만한",
#             "가볼만한",
#         ]

#         simplified = message.lower()

#         for stopword in stopwords:
#             simplified = simplified.replace(
#                 stopword,
#                 " ",
#             )

#         if category:
#             for keyword in CATEGORY_KEYWORDS[category]:
#                 simplified = simplified.replace(
#                     keyword,
#                     " ",
#                 )

#         simplified = " ".join(
#             simplified.split()
#         )

#         return simplified or message

#     @staticmethod
#     def _create_fallback_answer(
#         message: str,
#         category: str | None,
#         search_results: list[dict[str, Any]],
#     ) -> str:
#         """
#         OpenAI API 장애나 키 미설정 시 사용할 기본 답변입니다.
#         """

#         if not search_results:
#             return (
#                 f"'{message}'와 관련된 정보를 "
#                 "제공 데이터에서 찾지 못했습니다. "
#                 "지역명이나 장소 유형을 조금 더 "
#                 "구체적으로 입력해 주세요."
#             )

#         category_text = category or "지역 정보"

#         place_descriptions = []

#         for place in search_results:
#             title = place["title"]
#             address = place["address"]

#             if address:
#                 place_descriptions.append(
#                     f"{title}({address})"
#                 )
#             else:
#                 place_descriptions.append(title)

#         joined_places = ", ".join(
#             place_descriptions
#         )

#         return (
#             f"{category_text} 관련 장소를 "
#             f"{len(search_results)}곳 찾았습니다. "
#             f"{joined_places}입니다."
#         )


# chatbot_service = ChatbotService()

from typing import Any

from app.schemas.chat import ChatMessage
from app.services.openai_service import openai_service
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


CONTEXTUAL_EXPRESSIONS = [
    "그중",
    "그 중",
    "거기",
    "그곳",
    "그 장소",
    "첫 번째",
    "첫번째",
    "두 번째",
    "두번째",
    "마지막",
    "위에서",
    "방금",
    "앞에서",
    "그거",
    "그건",
    "그곳들",
]


class ChatbotService:
    """지역 관광정보 챗봇 서비스."""

    async def answer(
        self,
        message: str,
        history: list[ChatMessage],
        limit: int = 5,
    ) -> dict[str, Any]:
        normalized_message = message.strip()

        # 현재 질문만으로 카테고리를 먼저 찾습니다.
        category = self._detect_category(normalized_message)

        # 현재 질문에 카테고리가 없다면 이전 대화에서 찾습니다.
        if category is None:
            category = self._detect_category_from_history(history)

        # "그중에서", "첫 번째"와 같은 후속 질문이면
        # 이전 질문과 현재 질문을 합쳐 검색합니다.
        search_query = self._build_search_query(
            message=normalized_message,
            history=history,
        )

        print(f"[ChatbotService] 검색 문장: {search_query}")
        print(f"[ChatbotService] 추론 카테고리: {category}")

        search_results = tourism_search_service.search(
            query=search_query,
            category=category,
            limit=limit,
        )

        # 첫 번째 검색 결과가 없으면 불필요한 표현을 제거해 재검색합니다.
        if not search_results:
            simplified_query = self._simplify_query(
                message=search_query,
                category=category,
            )

            print(
                "[ChatbotService] 단순화 검색 문장: "
                f"{simplified_query}"
            )

            search_results = tourism_search_service.search(
                query=simplified_query,
                category=category,
                limit=limit,
            )

        # 후속 질문인데도 결과가 없다면 현재 질문만으로 한 번 더 검색합니다.
        if (
            not search_results
            and search_query != normalized_message
        ):
            current_query = self._simplify_query(
                message=normalized_message,
                category=category,
            )

            search_results = tourism_search_service.search(
                query=current_query,
                category=category,
                limit=limit,
            )

        if openai_service.is_available():
            try:
                answer_text = await openai_service.generate_answer(
                    message=normalized_message,
                    history=history,
                    search_results=search_results,
                )

            except RuntimeError as error:
                print(f"[OpenAI 응답 오류] {error}")

                answer_text = self._create_fallback_answer(
                    message=normalized_message,
                    category=category,
                    search_results=search_results,
                )

        else:
            print(
                "[경고] OPENAI_API_KEY가 없어 "
                "기본 답변을 반환합니다."
            )

            answer_text = self._create_fallback_answer(
                message=normalized_message,
                category=category,
                search_results=search_results,
            )

        return {
            "answer": answer_text,
            "places": search_results,
        }

    @staticmethod
    def _detect_category(
        message: str,
    ) -> str | None:
        """문장에서 관광 카테고리를 추론합니다."""

        lowered_message = message.lower()

        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in lowered_message:
                    return category

        return None

    @classmethod
    def _detect_category_from_history(
        cls,
        history: list[ChatMessage],
    ) -> str | None:
        """
        현재 질문에 카테고리가 없을 때
        최근 사용자 대화에서 카테고리를 찾습니다.
        """

        for chat_message in reversed(history):
            if chat_message.role != "user":
                continue

            category = cls._detect_category(
                chat_message.content
            )

            if category:
                return category

        return None

    @staticmethod
    def _is_contextual_followup(
        message: str,
    ) -> bool:
        """
        현재 질문이 이전 대화에 의존하는 후속 질문인지 판단합니다.
        """

        lowered_message = message.lower()

        return any(
            expression in lowered_message
            for expression in CONTEXTUAL_EXPRESSIONS
        )

    @classmethod
    def _build_search_query(
        cls,
        message: str,
        history: list[ChatMessage],
    ) -> str:
        """
        후속 질문이면 최근 사용자 질문과 현재 질문을 합칩니다.

        예:
        이전: 유성구 카페 추천해줘
        현재: 그중에서 주소가 지족동인 곳은?

        결과:
        유성구 카페 추천해줘 그중에서 주소가 지족동인 곳은?
        """

        if not history:
            return message

        if not cls._is_contextual_followup(message):
            return message

        previous_user_message = cls._find_previous_user_message(
            history
        )

        if not previous_user_message:
            return message

        return f"{previous_user_message} {message}"

    @staticmethod
    def _find_previous_user_message(
        history: list[ChatMessage],
    ) -> str | None:
        """가장 최근 사용자 메시지를 반환합니다."""

        for chat_message in reversed(history):
            if chat_message.role == "user":
                return chat_message.content.strip()

        return None

    @staticmethod
    def _simplify_query(
        message: str,
        category: str | None,
    ) -> str:
        """검색에 불필요한 표현을 제거합니다."""

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
            "어디야",
            "뭐가 있어",
            "뭐가 있나요",
            "갈 만한",
            "가볼 만한",
            "가볼만한",
            "주소가",
            "주소는",
            "곳은",
            "곳이야",
            "인가요",
            "이야",
        ]

        simplified = message.lower()

        for stopword in stopwords:
            simplified = simplified.replace(
                stopword,
                " ",
            )

        # 카테고리 단어를 전부 제거하면 검색 정확도가
        # 오히려 떨어질 수 있어 대표 키워드 하나는 유지합니다.
        if category:
            category_keywords = CATEGORY_KEYWORDS[category]

            for keyword in category_keywords:
                if keyword == category:
                    continue

                simplified = simplified.replace(
                    keyword,
                    " ",
                )

        # 후속 질문 표현도 제거합니다.
        for expression in CONTEXTUAL_EXPRESSIONS:
            simplified = simplified.replace(
                expression,
                " ",
            )

        simplified = " ".join(
            simplified.split()
        )

        return simplified or message

    @staticmethod
    def _create_fallback_answer(
        message: str,
        category: str | None,
        search_results: list[dict[str, Any]],
    ) -> str:
        """OpenAI API 장애 시 사용할 기본 답변입니다."""

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