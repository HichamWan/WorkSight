import os

class Settings:
    # In production, you would load these from environment variables
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SUPER_SECRET_SECURITY_KEY_FOR_WORKSIGHT_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Tokens automatically expire in 1 hour

settings = Settings()
