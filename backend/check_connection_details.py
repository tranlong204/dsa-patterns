#!/usr/bin/env python3
"""Check connection details and verify we're connecting to the right database"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Current RDS connection details:")
print(f"  Host: {os.getenv('RDS_HOST')}")
print(f"  Port: {os.getenv('RDS_PORT', '5432')}")
print(f"  Database: {os.getenv('RDS_DATABASE')}")
print(f"  User: {os.getenv('RDS_USER')}")
print(f"\nPlease verify in your database client that you're connecting to:")
print(f"  Host: {os.getenv('RDS_HOST')}")
print(f"  Database: {os.getenv('RDS_DATABASE')}")
print(f"  Schema: public (default)")
print(f"\nTry running: SELECT COUNT(*) FROM problems;")
print("You should see: 1432")

