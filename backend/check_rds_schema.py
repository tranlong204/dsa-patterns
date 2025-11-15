#!/usr/bin/env python3
"""Check if RDS database schema is set up"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("RDS_HOST"),
        port=int(os.getenv("RDS_PORT", 5432)),
        database=os.getenv("RDS_DATABASE"),
        user=os.getenv("RDS_USER"),
        password=os.getenv("RDS_PASSWORD")
    )
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    required_tables = ['problems', 'user_progress', 'company_tags', 'problem_company_tags']
    
    print("Tables found in RDS:")
    for table in tables:
        print(f"  ✓ {table}")
    
    print("\nRequired tables for migration:")
    missing = []
    for table in required_tables:
        if table in tables:
            print(f"  ✓ {table}")
        else:
            print(f"  ✗ {table} - MISSING")
            missing.append(table)
    
    if missing:
        print(f"\n⚠️  Missing tables: {', '.join(missing)}")
        print("Please run the SQL from 'supabase_migration.sql' on your RDS database first.")
        exit(1)
    else:
        print("\n✓ All required tables exist. Ready to migrate!")
        exit(0)
        
except Exception as e:
    print(f"✗ Error connecting to RDS: {e}")
    exit(1)

