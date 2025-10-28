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
    
    class Config:
        env_file = ".env"

settings = Settings()

