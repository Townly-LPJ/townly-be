import json
from pathlib import Path
from typing import Any


# tourism_search.py 기준:
# app/services/tourism_search.py
# 프로젝트 루트/data/*.json
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


CATEGORY_FILES = {
    "관광지": "대전_충청권_관광지.json",
    "레포츠": "대전_충청권_레포츠.json",
    "문화시설": "대전_충청권_문화시설.json",
    "쇼핑": "대전_충청권_쇼핑.json",
    "숙박": "대전_충청권_숙박.json",
    "여행코스": "대전_충청권_여행코스.json",
    "음식점": "대전_충청권_음식점.json",
    "축제공연행사": "대전_충청권_축제공연행사.json",
}


class TourismSearchService:
    """대전·충청권 관광 JSON 검색 서비스."""

    def __init__(self) -> None:
        self.locations: list[dict[str, Any]] = []
        self._load_json_files()

    def _load_json_files(self) -> None:
        """data 폴더의 관광 JSON 파일을 메모리에 적재합니다."""

        loaded_locations: list[dict[str, Any]] = []

        for category, filename in CATEGORY_FILES.items():
            file_path = DATA_DIR / filename

            if not file_path.exists():
                print(f"[경고] 데이터 파일을 찾을 수 없습니다: {file_path}")
                continue

            try:
                with file_path.open(
                    mode="r",
                    encoding="utf-8",
                ) as file:
                    raw_data = json.load(file)

            except (json.JSONDecodeError, OSError) as error:
                print(f"[경고] JSON 파일 로딩 실패: {file_path}")
                print(error)
                continue

            items = raw_data.get("items", [])

            for item in items:
                normalized_item = {
                    "content_id": str(item.get("contentid", "")),
                    "category": category,
                    "title": item.get("title", ""),
                    "address": self._combine_address(
                        item.get("addr1", ""),
                        item.get("addr2", ""),
                    ),
                    "telephone": item.get("tel", ""),
                    "longitude": self._to_float(item.get("mapx")),
                    "latitude": self._to_float(item.get("mapy")),
                    "image_url": (
                        item.get("firstimage")
                        or item.get("firstimage2")
                        or ""
                    ),
                }

                loaded_locations.append(normalized_item)

        self.locations = loaded_locations

        print(
            f"[TourismSearchService] "
            f"{len(self.locations)}개의 지역 데이터를 불러왔습니다."
        )

    @staticmethod
    def _combine_address(addr1: str, addr2: str) -> str:
        """기본 주소와 상세 주소를 합칩니다."""

        return " ".join(
            part.strip()
            for part in [addr1, addr2]
            if part and part.strip()
        )

    @staticmethod
    def _to_float(value: Any) -> float | None:
        """문자열 좌표를 float로 변환합니다."""

        if value in (None, ""):
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def search(
        self,
        query: str,
        category: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        제목, 주소, 카테고리를 기준으로 검색합니다.

        점수:
        - 제목에 전체 검색어 포함: +10
        - 주소에 전체 검색어 포함: +7
        - 개별 검색 단어가 제목에 포함: +4
        - 개별 검색 단어가 주소에 포함: +2
        - 검색 단어가 카테고리에 포함: +2
        """

        normalized_query = query.strip().lower()

        if not normalized_query:
            return []

        keywords = [
            keyword
            for keyword in normalized_query.split()
            if keyword
        ]

        scored_results: list[
            tuple[int, dict[str, Any]]
        ] = []

        for location in self.locations:
            if category and location["category"] != category:
                continue

            title = location["title"].lower()
            address = location["address"].lower()
            location_category = location["category"].lower()

            score = 0

            if normalized_query in title:
                score += 10

            if normalized_query in address:
                score += 7

            for keyword in keywords:
                if keyword in title:
                    score += 4

                if keyword in address:
                    score += 2

                if keyword in location_category:
                    score += 2

            if score > 0:
                scored_results.append((score, location))

        scored_results.sort(
            key=lambda result: result[0],
            reverse=True,
        )

        return [
            location
            for _, location in scored_results[:limit]
        ]
    
    def search_advanced(
        self,
        query: str,
        category: str | None = None,
        locations: list[str] | None = None,
        detail_keywords: list[str] | None = None,
        require_image: bool = False,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        카테고리, 지역, 세부 키워드 조건을 분리하여 검색합니다.

        지역 조건은 모두 만족해야 합니다.
        예: ["유성구", "지족동"]
        → 주소에 유성구와 지족동이 모두 포함되어야 함
        """

        locations = locations or []
        detail_keywords = detail_keywords or []

        filtered_locations: list[dict[str, Any]] = []

        for location in self.locations:
            if (
                category
                and location["category"] != category
            ):
                continue

            address = location["address"].lower()
            title = location["title"].lower()
            image_url = location["image_url"]

            # 추출한 지역 조건을 모두 만족해야 합니다.
            if locations:
                matches_all_locations = all(
                    region.lower() in address
                    for region in locations
                )

                if not matches_all_locations:
                    continue

            if require_image and not image_url:
                continue

            # 세부 키워드는 별도 점수 계산에 활용합니다.
            score = 0

            for keyword in detail_keywords:
                lowered_keyword = keyword.lower()

                if lowered_keyword in title:
                    score += 10

                if lowered_keyword in address:
                    score += 3

                # 카페 데이터에는 제목에 카페가 직접 없고
                # 커피 또는 베이커리만 있을 수도 있습니다.
                if lowered_keyword == "카페":
                    cafe_synonyms = [
                        "카페",
                        "커피",
                        "베이커리",
                    ]

                    if any(
                        synonym in title
                        for synonym in cafe_synonyms
                    ):
                        score += 8

            # 일반 검색어도 보조 점수로 사용합니다.
            query_keywords = [
                keyword
                for keyword in query.lower().split()
                if keyword
            ]

            for keyword in query_keywords:
                if keyword in title:
                    score += 4

                if keyword in address:
                    score += 2

            # 지역 및 카테고리 조건은 만족했지만
            # 제목 키워드가 없는 경우도 후보에 포함합니다.
            if locations or category:
                score += 1

            filtered_locations.append(
                {
                    "score": score,
                    "place": location,
                }
            )

        filtered_locations.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return [
            item["place"]
            for item in filtered_locations[:limit]
        ]    

    def get_by_category(
        self,
        category: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """특정 카테고리의 장소를 반환합니다."""

        return [
            location
            for location in self.locations
            if location["category"] == category
        ][:limit]


tourism_search_service = TourismSearchService()