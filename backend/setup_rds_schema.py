#!/usr/bin/env python3
"""Set up RDS database schema by running SQL migration"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Read SQL file
sql_file = "supabase_migration.sql"
try:
    with open(sql_file, 'r') as f:
        sql_content = f.read()
except FileNotFoundError:
    print(f"✗ SQL file '{sql_file}' not found")
    exit(1)

# Connect to RDS
try:
    conn = psycopg2.connect(
        host=os.getenv("RDS_HOST"),
        port=int(os.getenv("RDS_PORT", 5432)),
        database=os.getenv("RDS_DATABASE"),
        user=os.getenv("RDS_USER"),
        password=os.getenv("RDS_PASSWORD")
    )
    
    cursor = conn.cursor()
    
    # Execute SQL (split by semicolons, but handle multi-line statements)
    # For simplicity, execute the entire file
    print("Setting up database schema...")
    cursor.execute(sql_content)
    conn.commit()
    
    # Verify tables were created
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    print(f"✓ Schema setup complete!")
    print(f"✓ Created {len(tables)} tables: {', '.join(tables)}")
    print("\nReady to run migration!")
    
except psycopg2.Error as e:
    print(f"✗ Database error: {e}")
    if "already exists" in str(e).lower():
        print("(Some objects may already exist - this is okay)")
    exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

