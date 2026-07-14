from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.post import Post, PostCategory
from app.schemas.post import (
    PostCreate,
    PostUpdate,
)
from app.utils.password import (
    hash_password,
    verify_password,
)


def create_post(
    db: Session,
    request: PostCreate,
) -> Post:
    post = Post(
        category=request.category.value,
        title=request.title,
        content=request.content,
        nickname=request.nickname,
        password_hash=hash_password(request.password),
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


def get_posts(
    db: Session,
    category: PostCategory | None = None,
) -> list[Post]:
    statement = select(Post)

    if category is not None:
        statement = statement.where(
            Post.category == category.value,
        )

    statement = statement.order_by(
        Post.created_at.desc()
    )

    return list(db.scalars(statement).all())


def get_post(
    db: Session,
    post_id: int,
) -> Post | None:
    statement = select(Post).where(
        Post.id == post_id
    )

    return db.scalar(statement)


def update_post(
    db: Session,
    post: Post,
    request: PostUpdate,
) -> Post | None:
    
    # 비밀번호 검증
    if not verify_password(
        request.password,
        post.password_hash,
    ):
        return None

    post.category = request.category.value
    post.title = request.title
    post.content = request.content

    db.commit()
    db.refresh(post)

    return post


def delete_post(
    db: Session,
    post: Post,
    password: str,
) -> bool:

    # 비밀번호 검증
    if not verify_password(
        password,
        post.password_hash,
    ):
        return False

    db.delete(post)
    db.commit()

    return True