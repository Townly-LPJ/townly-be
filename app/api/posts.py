from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.post import PostCategory
from app.schemas.post import (
    PostCreate,
    PostListResponse,
    PostResponse,
)
from app.services.post_service import (
    create_post,
    get_post,
    get_posts,
)


router = APIRouter(
    prefix="/api/posts",
    tags=["posts"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post_api(
    request: PostCreate,
    db: DbSession,
) -> PostResponse:
    return create_post(db, request)


@router.get(
    "",
    response_model=list[PostListResponse],
)
def get_posts_api(
    db: DbSession,
    category: PostCategory | None = Query(default=None),
) -> list[PostListResponse]:
    return get_posts(db, category)


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
def get_post_api(
    post_id: int,
    db: DbSession,
) -> PostResponse:
    post = get_post(db, post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    return post