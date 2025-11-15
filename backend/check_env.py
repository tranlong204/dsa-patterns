#!/usr/bin/env python3
"""Check if required environment variables are set"""
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = {
    'Supabase': ['SUPABASE_URL', 'SUPABASE_KEY'],
    'RDS': ['RDS_HOST', 'RDS_DATABASE', 'RDS_USER', 'RDS_PASSWORD']
}

print("Checking environment variables...\n")

all_set = True
for category, vars_list in required_vars.items():
    print(f"{category} variables:")
    for var in vars_list:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'PASSWORD' in var or 'KEY' in var:
                print(f"  ✓ {var}: {'*' * 10}")
            else:
                print(f"  ✓ {var}: {value}")
        else:
            print(f"  ✗ {var}: NOT SET")
            all_set = False
    print()

if all_set:
    print("✓ All required environment variables are set!")
    print("You can proceed with the migration.")
else:
    print("✗ Some environment variables are missing.")
    print("\nPlease add the following to your .env file:")
    print("\n# Supabase (source)")
    print("SUPABASE_URL=your_supabase_url")
    print("SUPABASE_KEY=your_supabase_key")
    print("\n# RDS (destination)")
    print("RDS_HOST=your-rds-endpoint.region.rds.amazonaws.com")
    print("RDS_PORT=5432")
    print("RDS_DATABASE=dsapatterns")
    print("RDS_USER=admin")
    print("RDS_PASSWORD=your_rds_password")

