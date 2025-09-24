"""Database service for centralized database operations."""

import pymysql
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

from config.database import DatabaseConfig, TABLE_SCHEMA
from config.logging_config import logger


class DatabaseService:
    """Centralized database service for all database operations."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """Initialize database service with configuration."""
        self.config = config or DatabaseConfig.from_environment()
        
        if not self.config.validate():
            logger.error("Invalid database configuration")
            raise ValueError("Database configuration is incomplete")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        connection = None
        try:
            connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"Connected to database: {self.config.host}:{self.config.port}/{self.config.database}")
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                connection.close()
                logger.debug("Database connection closed")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results."""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    logger.debug(f"Query executed successfully, returned {len(results)} rows")
                    return results
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute an UPDATE/INSERT/DELETE query and return affected rows."""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    affected_rows = cursor.execute(query, params)
                    connection.commit()
                    logger.info(f"Query executed successfully, affected {affected_rows} rows")
                    return affected_rows
        except Exception as e:
            logger.error(f"Error executing update query: {e}")
            raise
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str = "workout_summary") -> int:
        """Insert DataFrame rows into the specified table."""
        if df.empty:
            logger.warning("Attempted to insert empty DataFrame")
            return 0
        
        # Prepare data
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        data = [tuple(x) for x in df.replace({np.nan: None}).values]
        
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    affected_rows = cursor.executemany(sql, data)
                    connection.commit()
                    logger.info(f"Inserted {affected_rows} rows into {table_name}")
                    return affected_rows
        except Exception as e:
            logger.error(f"Error inserting DataFrame into {table_name}: {e}")
            raise
    
    def create_database_if_not_exists(self) -> bool:
        """Create the database if it doesn't exist."""
        try:
            # Connect without specifying database
            connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password
            )
            
            with connection.cursor() as cursor:
                # Check if database exists
                cursor.execute("SHOW DATABASES")
                databases = [db[0] for db in cursor.fetchall()]
                
                if self.config.database not in databases:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.database}")
                    logger.info(f"Created database: {self.config.database}")
                    return True
                else:
                    logger.info(f"Database {self.config.database} already exists")
                    return False
            
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def create_tables_if_not_exist(self) -> None:
        """Create all required tables if they don't exist."""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    for table_name, schema in TABLE_SCHEMA.items():
                        cursor.execute(schema)
                        logger.info(f"Ensured table {table_name} exists")
                    connection.commit()
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def get_table_info(self, table_name: str = "workout_summary") -> Dict[str, Any]:
        """Get information about a table (row count, last workout date, etc.)."""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                    row_count = cursor.fetchone()['count']
                    
                    # Get last workout date (if any rows exist)
                    last_workout = None
                    if row_count > 0:
                        cursor.execute(f"SELECT workout_date FROM {table_name} ORDER BY workout_date DESC LIMIT 1")
                        result = cursor.fetchone()
                        if result:
                            last_workout = result['workout_date']
                    
                    info = {
                        'table_name': table_name,
                        'row_count': row_count,
                        'last_workout_date': last_workout
                    }
                    
                    logger.debug(f"Table info for {table_name}: {info}")
                    return info
                    
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    logger.info("Database connection test successful")
                    return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False