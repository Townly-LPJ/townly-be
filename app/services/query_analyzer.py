from dataclasses import dataclass, field

from app.schemas.chat import ChatMessage


CATEGORY_KEYWORDS = {
    "관광지": [
        "관광지",
        "관광",
        "명소",
        "볼거리",
        "나들이",
        "가볼만한 곳",
        "가볼 만한 곳",
    ],
    "음식점": [
        "음식점",
        "식당",
        "맛집",
        "밥집",
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
        "코스",
        "동선",
        "일정",
    ],
}


# 이번 프로젝트 데이터에 포함된 주요 지역입니다.
# 이후 필요하면 지역을 추가하면 됩니다.
KNOWN_LOCATIONS = [
    "대전광역시",
    "대전",
    "세종특별자치시",
    "세종",
    "공주시",
    "공주",
    "계룡시",
    "계룡",
    "논산시",
    "논산",
    "옥천군",
    "옥천",
    "유성구",
    "서구",
    "중구",
    "동구",
    "대덕구",
    "지족동",
    "외삼동",
    "봉명동",
    "궁동",
    "관평동",
    "도룡동",
    "둔산동",
    "은행동",
    "대흥동",
    "원신흥동",
    "전민동",
    "하기동",
    "노은동",
]


FOLLOWUP_EXPRESSIONS = [
    "그중",
    "그 중",
    "거기",
    "그곳",
    "그 장소",
    "그거",
    "첫 번째",
    "첫번째",
    "두 번째",
    "두번째",
    "마지막",
    "방금",
    "위에서",
    "앞에서",
]


@dataclass
class QueryConditions:
    """사용자 질문에서 추출한 검색 조건."""

    original_message: str
    search_text: str
    category: str | None = None
    locations: list[str] = field(default_factory=list)
    detail_keywords: list[str] = field(default_factory=list)
    require_image: bool = False
    is_followup: bool = False


class QueryAnalyzer:
    """사용자 질문을 검색 조건으로 변환합니다."""

    def analyze(
        self,
        message: str,
        history: list[ChatMessage],
    ) -> QueryConditions:
        normalized_message = message.strip()

        is_followup = self._is_followup(normalized_message)

        previous_user_message = (
            self._find_previous_user_message(history)
            if is_followup
            else None
        )

        context_text = normalized_message

        if previous_user_message:
            context_text = (
                f"{previous_user_message} {normalized_message}"
            )

        category = self._extract_category(context_text)
        locations = self._extract_locations(context_text)
        detail_keywords = self._extract_detail_keywords(context_text)
        require_image = self._requires_image(normalized_message)

        search_text = self._build_search_text(
            locations=locations,
            detail_keywords=detail_keywords,
        )

        return QueryConditions(
            original_message=normalized_message,
            search_text=search_text,
            category=category,
            locations=locations,
            detail_keywords=detail_keywords,
            require_image=require_image,
            is_followup=is_followup,
        )

    @staticmethod
    def _extract_category(
        text: str,
    ) -> str | None:
        lowered_text = text.lower()

        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in lowered_text:
                    return category

        return None

    @staticmethod
    def _extract_locations(
        text: str,
    ) -> list[str]:
        found_locations: list[str] = []

        # 긴 지역명부터 확인해야
        # "대전광역시"가 "대전"보다 먼저 처리됩니다.
        sorted_locations = sorted(
            KNOWN_LOCATIONS,
            key=len,
            reverse=True,
        )

        for location in sorted_locations:
            if location not in text:
                continue

            # 예: 대전광역시와 대전이 동시에 들어가는 것을 방지
            if any(
                location in saved_location
                or saved_location in location
                for saved_location in found_locations
            ):
                continue

            found_locations.append(location)

        return found_locations

    @staticmethod
    def _extract_detail_keywords(
        text: str,
    ) -> list[str]:
        detail_groups = {
            "카페": [
                "카페",
                "커피",
                "베이커리",
                "빵집",
            ],
            "호텔": [
                "호텔",
            ],
            "박물관": [
                "박물관",
            ],
            "미술관": [
                "미술관",
            ],
            "도서관": [
                "도서관",
            ],
            "시장": [
                "시장",
            ],
            "마트": [
                "마트",
            ],
            "공원": [
                "공원",
            ],
        }

        lowered_text = text.lower()
        keywords: list[str] = []

        for representative, synonyms in detail_groups.items():
            if any(
                synonym in lowered_text
                for synonym in synonyms
            ):
                keywords.append(representative)

        return keywords

    @staticmethod
    def _requires_image(
        message: str,
    ) -> bool:
        image_expressions = [
            "이미지가 있는",
            "사진이 있는",
            "이미지 있는",
            "사진 있는",
            "사진 보여",
        ]

        return any(
            expression in message
            for expression in image_expressions
        )

    @staticmethod
    def _is_followup(
        message: str,
    ) -> bool:
        return any(
            expression in message
            for expression in FOLLOWUP_EXPRESSIONS
        )

    @staticmethod
    def _find_previous_user_message(
        history: list[ChatMessage],
    ) -> str | None:
        for chat_message in reversed(history):
            if chat_message.role == "user":
                return chat_message.content.strip()

        return None

    @staticmethod
    def _build_search_text(
        locations: list[str],
        detail_keywords: list[str],
    ) -> str:
        values = locations + detail_keywords

        return " ".join(values)


query_analyzer = QueryAnalyzer()