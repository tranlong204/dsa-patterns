#!/usr/bin/env python3
"""Create database if it doesn't exist"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

# Connect to postgres database to create new database
try:
    conn = psycopg2.connect(
        host=os.getenv("RDS_HOST"),
        port=int(os.getenv("RDS_PORT", 5432)),
        database="postgres",  # Connect to default postgres database
        user=os.getenv("RDS_USER"),
        password=os.getenv("RDS_PASSWORD")
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    db_name = os.getenv("RDS_DATABASE")
    
    # Check if database exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()
    
    if exists:
        print(f"✓ Database '{db_name}' already exists")
    else:
        # Create database
        cursor.execute(f'CREATE DATABASE "{db_name}"')
        print(f"✓ Created database '{db_name}'")
    
    cursor.close()
    conn.close()
    
    print("\nNext steps:")
    print("1. Connect to the database and run the SQL from 'supabase_migration.sql'")
    print("2. Then run the migration script: python migrate_to_rds.py")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nPossible issues:")
    print("- Database server is not accessible")
    print("- Credentials are incorrect")
    print("- Security group doesn't allow connections from your IP")

