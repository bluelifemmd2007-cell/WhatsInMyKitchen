import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./kitchen.db")

    MIN_MATCH_PERCENT: float = float(os.getenv("MIN_MATCH_PERCENT", "30"))
    MAX_RESULTS: int = int(os.getenv("MAX_RESULTS", "10"))


settings = Settings()

if not settings.GROQ_API_KEY:
    print(
        "[WARNING] GROQ_API_KEY is not set. "
        "The database-matching feature will still work, but AI-generated "
        "creative recipes will fail until you add a key to your .env file."
    )