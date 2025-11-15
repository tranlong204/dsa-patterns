"""
Database connection for AWS RDS PostgreSQL
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from typing import Generator
import json

# Connection pool for RDS
_pool = None

def get_db_config():
    """Get database configuration from environment variables"""
    return {
        'host': os.getenv('RDS_HOST'),
        'port': int(os.getenv('RDS_PORT', 5432)),
        'database': os.getenv('RDS_DATABASE'),
        'user': os.getenv('RDS_USER'),
        'password': os.getenv('RDS_PASSWORD'),
    }

def init_pool():
    """Initialize connection pool"""
    global _pool
    if _pool is None:
        config = get_db_config()
        _pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=5,
            **config
        )
    return _pool

@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """Get a database connection from the pool"""
    pool = init_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

def get_db_cursor(conn=None):
    """Get a database cursor with RealDictCursor for dict-like results"""
    if conn:
        return conn.cursor(cursor_factory=RealDictCursor)
    else:
        with get_db_connection() as conn:
            return conn.cursor(cursor_factory=RealDictCursor)

class RDSClient:
    """RDS client that mimics Supabase client interface"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def select(self, *columns):
        """Start a SELECT query"""
        return QueryBuilder(self.table_name, 'select', columns)
    
    def insert(self, data):
        """Insert data"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = list(data.values())
            
            # Handle JSON fields
            for i, (key, value) in enumerate(data.items()):
                if isinstance(value, (list, dict)):
                    values[i] = json.dumps(value)
            
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING *"
            cursor.execute(query, values)
            conn.commit()
            result = cursor.fetchone()
            cursor.close()
            return Response([dict(result)] if result else [])
    
    def update(self, data):
        """Start an UPDATE query"""
        return QueryBuilder(self.table_name, 'update', None, data)
    
    def delete(self):
        """Start a DELETE query"""
        return QueryBuilder(self.table_name, 'delete')
    
    def table(self, table_name: str):
        """Create a new client for a different table"""
        return RDSClient(table_name)

class QueryBuilder:
    """Query builder that mimics Supabase query interface"""
    
    def __init__(self, table_name: str, operation: str, columns=None, update_data=None):
        self.table_name = table_name
        self.operation = operation
        self.columns = columns or ['*']
        self.update_data = update_data
        self.conditions = []
        self.params = []
        self.param_counter = 1
        self.limit_val = None
        self.offset_val = None
        self.order_by = None
    
    def eq(self, column: str, value):
        """Add equality condition"""
        self.conditions.append(f"{column} = ${self.param_counter}")
        self.params.append(value)
        self.param_counter += 1
        return self
    
    def neq(self, column: str, value):
        """Add not-equal condition"""
        self.conditions.append(f"{column} != ${self.param_counter}")
        self.params.append(value)
        self.param_counter += 1
        return self
    
    def is_(self, column: str, value):
        """Add IS condition"""
        if value == "null":
            self.conditions.append(f"{column} IS NULL")
        else:
            self.conditions.append(f"{column} IS ${self.param_counter}")
            self.params.append(value)
            self.param_counter += 1
        return self
    
    def not_(self):
        """Negate next condition"""
        return self
    
    def in_(self, column: str, values: list):
        """Add IN condition"""
        placeholders = ', '.join([f'${i}' for i in range(self.param_counter, self.param_counter + len(values))])
        self.conditions.append(f"{column} IN ({placeholders})")
        self.params.extend(values)
        self.param_counter += len(values)
        return self
    
    def range(self, start: int, end: int):
        """Add LIMIT and OFFSET"""
        self.limit_val = end - start + 1
        self.offset_val = start
        return self
    
    def order(self, column: str, desc: bool = False):
        """Add ORDER BY"""
        self.order_by = f"{column} {'DESC' if desc else 'ASC'}"
        return self
    
    def execute(self):
        """Execute the query"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            if self.operation == 'select':
                columns_str = ', '.join(self.columns) if isinstance(self.columns, list) else '*'
                query = f"SELECT {columns_str} FROM {self.table_name}"
                
                if self.conditions:
                    # Replace $1, $2 with %s for psycopg2
                    where_clause = ' AND '.join(self.conditions).replace('$', '%')
                    query += f" WHERE {where_clause}"
                
                if self.order_by:
                    query += f" ORDER BY {self.order_by}"
                
                if self.limit_val:
                    query += f" LIMIT {self.limit_val}"
                if self.offset_val:
                    query += f" OFFSET {self.offset_val}"
                
                cursor.execute(query, self.params)
                results = cursor.fetchall()
                cursor.close()
                return Response([dict(row) for row in results])
            
            elif self.operation == 'update':
                # Build SET clause
                set_parts = []
                update_values = []
                param_idx = 1
                for key, value in self.update_data.items():
                    if isinstance(value, (list, dict)):
                        update_values.append(json.dumps(value))
                    else:
                        update_values.append(value)
                    set_parts.append(f"{key} = %s")
                
                query = f"UPDATE {self.table_name} SET {', '.join(set_parts)}"
                
                # Add WHERE clause
                if self.conditions:
                    where_clause = ' AND '.join(self.conditions).replace('$', '%')
                    query += f" WHERE {where_clause}"
                    update_values.extend(self.params)
                
                query += " RETURNING *"
                cursor.execute(query, update_values)
                conn.commit()
                results = cursor.fetchall()
                cursor.close()
                return Response([dict(row) for row in results])
            
            elif self.operation == 'delete':
                query = f"DELETE FROM {self.table_name}"
                if self.conditions:
                    where_clause = ' AND '.join(self.conditions).replace('$', '%')
                    query += f" WHERE {where_clause}"
                    cursor.execute(query, self.params)
                else:
                    cursor.execute(query)
                conn.commit()
                cursor.close()
                return Response([])

class Response:
    """Response object that mimics Supabase response"""
    def __init__(self, data):
        self.data = data

# Global RDS client instance
_rds_client = None

def get_rds_client():
    """Get RDS client instance"""
    global _rds_client
    if _rds_client is None:
        _rds_client = RDSClient('')
    return _rds_client

def get_supabase():
    """Get database client (RDS or Supabase based on environment)"""
    # Check if we're using RDS
    if os.getenv('RDS_HOST'):
        return get_rds_client()
    else:
        # Fallback to Supabase
        from app.database import get_supabase as get_supabase_original
        return get_supabase_original()

