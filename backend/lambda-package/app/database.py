"""
Database connection - supports both RDS and Supabase
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Check if using RDS or Supabase
USE_RDS = bool(os.getenv("RDS_HOST"))

if USE_RDS:
    # Use RDS PostgreSQL
    from app.database_rds import get_supabase
else:
    # Use Supabase (fallback)
    from supabase import create_client, Client
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Either RDS_HOST or (SUPABASE_URL and SUPABASE_KEY) must be set in environment variables")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    def get_supabase() -> Client:
        return supabase

