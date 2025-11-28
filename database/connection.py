"""
Database connection utilities for Retail Price Intelligence System.
"""
import os
from typing import Optional
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool


class DatabaseConnection:
    """Manages PostgreSQL database connections using connection pooling."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        min_conn: int = 1,
        max_conn: int = 10
    ):
        """
        Initialize database connection pool.
        
        Args:
            host: Database host (defaults to DB_HOST env var or 'localhost')
            port: Database port (defaults to DB_PORT env var or 5432)
            database: Database name (defaults to DB_NAME env var)
            user: Database user (defaults to DB_USER env var)
            password: Database password (defaults to DB_PASSWORD env var)
            min_conn: Minimum connections in pool
            max_conn: Maximum connections in pool
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', 5432))
        self.database = database or os.getenv('DB_NAME', 'retail_price_intelligence')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', '')
        
        self.pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool(min_conn, max_conn)
    
    def _initialize_pool(self, min_conn: int, max_conn: int):
        """Initialize the connection pool."""
        try:
            self.pool = SimpleConnectionPool(
                min_conn,
                max_conn,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
        except psycopg2.Error as e:
            raise ConnectionError(f"Failed to create database connection pool: {e}")
    
    @contextmanager
    def get_connection(self, cursor_factory=RealDictCursor):
        """
        Get a database connection from the pool.
        
        Usage:
            with db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM products")
                    result = cursor.fetchall()
        
        Args:
            cursor_factory: Cursor factory (defaults to RealDictCursor for dict-like results)
        
        Yields:
            Database connection
        """
        if self.pool is None:
            raise RuntimeError("Connection pool not initialized")
        
        conn = self.pool.getconn()
        try:
            conn.cursor_factory = cursor_factory
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """
        Get a cursor from the connection pool.
        
        Usage:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM products")
                result = cursor.fetchall()
        
        Args:
            cursor_factory: Cursor factory (defaults to RealDictCursor)
        
        Yields:
            Database cursor
        """
        with self.get_connection(cursor_factory) as conn:
            with conn.cursor() as cursor:
                yield cursor
    
    def execute_query(self, query: str, params: Optional[tuple] = None):
        """
        Execute a query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            Query results
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Optional[tuple] = None):
        """
        Execute an update/insert/delete query.
        
        Args:
            query: SQL query string
            params: Query parameters
        
        Returns:
            Number of affected rows
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def close(self):
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
            self.pool = None


db: Optional[DatabaseConnection] = None


def init_db(
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None
):
    """
    Initialize the global database connection.
    
    Args:
        host: Database host
        port: Database port
        database: Database name
        user: Database user
        password: Database password
    """
    global db
    db = DatabaseConnection(host, port, database, user, password)
    return db


def get_db() -> DatabaseConnection:
    """
    Get the global database connection instance.
    
    Returns:
        Database connection instance
    
    Raises:
        RuntimeError: If database not initialized
    """
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return db

