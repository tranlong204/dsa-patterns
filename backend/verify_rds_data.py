#!/usr/bin/env python3
"""Verify data in RDS database"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
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
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check row counts
    tables = ['problems', 'user_progress', 'company_tags', 'problem_company_tags']
    
    print("Checking data in RDS database...\n")
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        result = cursor.fetchone()
        count = result['count'] if result else 0
        print(f"{table}: {count} rows")
        
        # Show sample data for problems table
        if table == 'problems' and count > 0:
            cursor.execute(f"SELECT id, number, title, difficulty FROM {table} LIMIT 5")
            samples = cursor.fetchall()
            print("  Sample rows:")
            for row in samples:
                print(f"    ID: {row['id']}, Number: {row['number']}, Title: {row['title'][:50]}..., Difficulty: {row['difficulty']}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

