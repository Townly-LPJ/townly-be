# from fastapi import APIRouter, HTTPException, status

# from app.schemas.chat import ChatRequest, ChatResponse
# from app.services.chatbot_service import chatbot_service


# router = APIRouter(
#     prefix="/api/chat",
#     tags=["chat"],
# )


# @router.post(
#     "",
#     response_model=ChatResponse,
#     status_code=status.HTTP_200_OK,
#     summary="지역 정보 챗봇 질문",
# )
# async def chat(
#     request: ChatRequest,
# ) -> ChatResponse:
#     """
#     사용자 질문에 관련된 대전·충청권 지역 정보를 검색합니다.

#     현재 단계에서는 JSON 검색 결과를 임시 답변으로 반환합니다.
#     다음 단계에서 OpenAI API를 연결합니다.
#     """

#     try:
#         result = chatbot_service.answer(
#             message=request.message,
#         )

#         return ChatResponse(**result)

#     except Exception as error:
#         print(f"[Chat API 오류] {error}")

#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="챗봇 응답을 생성하는 중 오류가 발생했습니다.",
#         ) from error

from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chatbot_service import chatbot_service


router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="지역 정보 챗봇 질문",
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:
    """
    제공된 관광 JSON 데이터를 검색하고,
    검색 결과를 기반으로 챗봇 답변을 생성합니다.
    """

    try:
        result = await chatbot_service.answer(
            message=request.message,
            history=request.history,
        )

        return ChatResponse(**result)

    except Exception as error:
        print(
            f"[Chat API 오류] "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "챗봇 응답을 생성하는 중 "
                "오류가 발생했습니다."
            ),
        ) from error