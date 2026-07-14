import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """애플리케이션 환경설정."""

    OPENAI_API_KEY: str = os.getenv(
        "OPENAI_API_KEY",
        "",
    )

    OPENAI_MODEL: str = os.getenv(
        "OPENAI_MODEL",
        "gpt-4.1-mini",
    )


settings = Settings()