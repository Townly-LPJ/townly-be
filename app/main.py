from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.posts import router as posts_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import Post  # noqa: F401


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

# 라우터 등록보다 먼저 작성
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(posts_router)


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "message": "Townly API is running",
    }