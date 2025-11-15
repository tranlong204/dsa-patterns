"""
Database connection - supports both RDS and Supabase
"""
import os
import logging
from dotenv import load_dotenv

# Load .env file only for local development
# In Lambda, environment variables are set directly, so we don't want to override them
# override=False ensures Lambda env vars take precedence over .env file
load_dotenv(override=False)

logger = logging.getLogger(__name__)

# Lazy initialization - check at runtime, not import time
_supabase_client = None
_rds_client_imported = False

def get_supabase():
    """
    Get database client - checks RDS_HOST at runtime to decide between RDS and Supabase
    """
    global _supabase_client, _rds_client_imported
    
    # Check RDS_HOST at runtime (not import time)
    rds_host = os.getenv("RDS_HOST")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    logger.info(f"Database selection: RDS_HOST={bool(rds_host)}, SUPABASE_URL={bool(supabase_url)}")
    
    if rds_host:
        # Use RDS PostgreSQL
        if not _rds_client_imported:
            from app.database_rds import get_supabase as get_rds_supabase
            _rds_client_imported = True
            logger.info("Using RDS PostgreSQL database")
            return get_rds_supabase()
        else:
            from app.database_rds import get_supabase as get_rds_supabase
            return get_rds_supabase()
    else:
        # Use Supabase (fallback)
        if _supabase_client is None:
            if not supabase_url or not supabase_key:
                raise ValueError("Either RDS_HOST or (SUPABASE_URL and SUPABASE_KEY) must be set in environment variables")
            
            from supabase import create_client, Client
            _supabase_client = create_client(supabase_url, supabase_key)
            logger.info("Using Supabase database")
        
        return _supabase_client

