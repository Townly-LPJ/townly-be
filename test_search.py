from app.services.tourism_search import tourism_search_service


def main() -> None:
    print("전체 데이터 개수:")
    print(len(tourism_search_service.locations))

    print("\n유성구 카페 검색:")
    results = tourism_search_service.search(
        query="유성구 카페",
        category="음식점",
        limit=5,
    )

    for result in results:
        print(result)


if __name__ == "__main__":
    main()