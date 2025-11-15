"""
Script to initialize database tables in Supabase
This is a reference script - you need to run the SQL in Supabase SQL editor
"""
from app.database import get_supabase

def print_sql_instructions():
    """Print instructions for setting up the database"""
    
    print("=" * 80)
    print("SUPABASE DATABASE SETUP INSTRUCTIONS")
    print("=" * 80)
    print("\n1. Go to your Supabase project dashboard")
    print("2. Navigate to 'SQL Editor'")
    print("3. Click 'New Query'")
    print("4. Copy and paste the SQL from: backend/supabase_migration.sql")
    print("5. Click 'Run' to execute the SQL")
    print("\nAlternatively, you can create tables manually:")
    print("\nTable: problems")
    print("  Columns:")
    print("    - id (BIGSERIAL PRIMARY KEY)")
    print("    - number (INTEGER)")
    print("    - title (TEXT)")
    print("    - difficulty (VARCHAR)")
    print("    - topics (JSONB)")
    print("    - link (TEXT)")
    print("    - subtopic (TEXT)")
    print("\nTable: user_progress")
    print("  Columns:")
    print("    - id (BIGSERIAL PRIMARY KEY)")
    print("    - user_id (VARCHAR)")
    print("    - problem_id (INTEGER REFERENCES problems)")
    print("    - solved (BOOLEAN)")
    print("    - solved_at (DATE)")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    print_sql_instructions()
