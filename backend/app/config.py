import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    # Comma-separated list of allowed CORS origins
    _cors_origins_raw: str = os.getenv("CORS_ORIGINS", "")
    CORS_ORIGINS: List[str] = (
        [origin.strip() for origin in _cors_origins_raw.split(",") if origin.strip()]
        if _cors_origins_raw
        else ["*"]
    )
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change_me_dev_secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 days
    DEFAULT_USERNAME: str = os.getenv("DEFAULT_USERNAME", "admin")
    DEFAULT_PASSWORD_HASH: str = os.getenv("DEFAULT_PASSWORD_HASH", "")
    
    class Config:
        env_file = ".env"

settings = Settings()

