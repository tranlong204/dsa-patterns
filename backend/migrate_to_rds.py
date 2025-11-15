"""
Migration script to copy data from Supabase to AWS RDS PostgreSQL
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from supabase import create_client
import json
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client():
    """Get Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return create_client(url, key)

def get_rds_connection():
    """Get RDS PostgreSQL connection"""
    return psycopg2.connect(
        host=os.getenv("RDS_HOST"),
        port=int(os.getenv("RDS_PORT", 5432)),
        database=os.getenv("RDS_DATABASE"),
        user=os.getenv("RDS_USER"),
        password=os.getenv("RDS_PASSWORD")
    )

def migrate_table(supabase, rds_conn, table_name, batch_size=100):
    """Migrate a table from Supabase to RDS"""
    print(f"\nMigrating table: {table_name}")
    
    # Get all data from Supabase
    offset = 0
    total_migrated = 0
    
    while True:
        response = supabase.table(table_name).select("*").range(offset, offset + batch_size - 1).execute()
        
        if not response.data:
            break
        
        # Insert into RDS
        cursor = rds_conn.cursor()
        for row in response.data:
            try:
                columns = ', '.join(row.keys())
                placeholders = ', '.join(['%s'] * len(row))
                values = list(row.values())
                
                # Handle JSON fields
                for i, (key, value) in enumerate(row.items()):
                    if isinstance(value, (list, dict)):
                        values[i] = json.dumps(value)
                
                query = f"""
                    INSERT INTO {table_name} ({columns})
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """
                cursor.execute(query, values)
                total_migrated += 1
            except Exception as e:
                print(f"  Error inserting row {row.get('id', 'unknown')}: {e}")
                continue
        
        offset += batch_size
        if len(response.data) < batch_size:
            break
    
    rds_conn.commit()
    cursor.close()
    print(f"  Migrated {total_migrated} rows")

def main():
    """Main migration function"""
    print("Starting migration from Supabase to RDS...")
    
    # Get connections
    supabase = get_supabase_client()
    rds_conn = get_rds_connection()
    
    # Verify RDS schema exists (run supabase_migration.sql first)
    cursor = rds_conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    
    print(f"\nFound tables in RDS: {tables}")
    
    # Migrate each table
    tables_to_migrate = ['problems', 'user_progress', 'company_tags', 'problem_company_tags']
    
    for table in tables_to_migrate:
        if table in tables:
            try:
                migrate_table(supabase, rds_conn, table)
            except Exception as e:
                print(f"Error migrating {table}: {e}")
        else:
            print(f"Table {table} not found in RDS, skipping...")
    
    rds_conn.close()
    print("\nMigration completed!")

if __name__ == "__main__":
    main()

