#!/usr/bin/env python3
"""Show actual data from RDS to verify migration"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json

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
    
    print("=" * 80)
    print("RDS DATABASE VERIFICATION")
    print("=" * 80)
    print(f"\nConnected to: {os.getenv('RDS_HOST')}")
    print(f"Database: {os.getenv('RDS_DATABASE')}")
    print(f"Current schema: public\n")
    
    # Check current database and schema
    cursor.execute("SELECT current_database(), current_schema()")
    db_info = cursor.fetchone()
    print(f"Current database: {db_info['current_database']}")
    print(f"Current schema: {db_info['current_schema']}\n")
    
    # Show all tables
    cursor.execute("""
        SELECT table_name, 
               (SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    print("Tables in public schema:")
    for table in tables:
        print(f"  - {table['table_name']} ({table['column_count']} columns)")
    
    print("\n" + "=" * 80)
    print("ROW COUNTS")
    print("=" * 80)
    
    # Count rows in each table
    tables_to_check = ['problems', 'user_progress', 'company_tags', 'problem_company_tags']
    for table in tables_to_check:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        result = cursor.fetchone()
        count = result['count'] if result else 0
        print(f"{table}: {count} rows")
    
    print("\n" + "=" * 80)
    print("SAMPLE DATA FROM PROBLEMS TABLE")
    print("=" * 80)
    
    cursor.execute("""
        SELECT id, number, title, difficulty, topics, link 
        FROM problems 
        ORDER BY id 
        LIMIT 10
    """)
    problems = cursor.fetchall()
    
    if problems:
        print(f"\nShowing first 10 problems:\n")
        for p in problems:
            topics_str = json.dumps(p['topics']) if isinstance(p['topics'], (dict, list)) else str(p['topics'])
            print(f"ID: {p['id']}")
            print(f"  Number: {p['number']}")
            print(f"  Title: {p['title']}")
            print(f"  Difficulty: {p['difficulty']}")
            print(f"  Topics: {topics_str[:50]}...")
            print(f"  Link: {p['link']}")
            print()
    else:
        print("No problems found!")
    
    print("=" * 80)
    print("SAMPLE DATA FROM USER_PROGRESS TABLE")
    print("=" * 80)
    
    cursor.execute("SELECT * FROM user_progress LIMIT 5")
    progress = cursor.fetchall()
    
    if progress:
        print(f"\nShowing first 5 user_progress entries:\n")
        for p in progress:
            print(f"ID: {p['id']}, User: {p['user_id']}, Problem ID: {p['problem_id']}, Solved: {p['solved']}, Solved At: {p.get('solved_at', 'NULL')}")
    else:
        print("No user_progress entries found!")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✓ Verification complete!")
    print("=" * 80)
    print("\nIf you don't see data in your database client:")
    print("1. Make sure you're connected to: dsa-patterns.cxm66ak2grwu.us-west-1.rds.amazonaws.com")
    print("2. Make sure you're using database: dsa-patterns")
    print("3. Make sure you're viewing schema: public")
    print("4. Try refreshing your database client")
    print("5. Try running: SELECT * FROM problems LIMIT 10;")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

