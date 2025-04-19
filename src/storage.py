"""
storage.py

This module provides storage adapters for persisting session data.
Currently implements a SQLite-based storage solution for local development.
"""

from abc import ABC, abstractmethod
import sqlite3
import json
import os
from typing import Dict, Optional, Any
from datetime import datetime

class StorageAdapter(ABC):
    """
    Abstract base class that defines the interface for storage adapters.
    All concrete storage implementations must implement these methods.
    """
    
    @abstractmethod
    def save_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Save session data to storage.
        
        Args:
            session_id (str): Unique session identifier
            data (Dict[str, Any]): Session data to store
        """
        pass
    
    @abstractmethod
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data from storage.
        
        Args:
            session_id (str): Unique session identifier
        
        Returns:
            Optional[Dict[str, Any]]: Session data if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """
        Delete session data from storage.
        
        Args:
            session_id (str): Unique session identifier
        """
        pass

class SQLiteAdapter(StorageAdapter):
    """SQLite implementation of the storage adapter for local development."""
    
    def __init__(self, db_path: str = "sessions.db"):
        """
        Initialize SQLite database.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Create sessions table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Save session data to SQLite.
        
        Args:
            session_id (str): Unique session identifier
            data (Dict[str, Any]): Session data to store
        """
        serialized_data = json.dumps(data)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions (session_id, data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                    data = excluded.data,
                    updated_at = CURRENT_TIMESTAMP
            """, (session_id, serialized_data))
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data from SQLite.
        
        Args:
            session_id (str): Unique session identifier
        
        Returns:
            Optional[Dict[str, Any]]: Session data if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT data FROM sessions WHERE session_id = ?",
                    (session_id,)
                )
                result = cursor.fetchone()
                return json.loads(result[0]) if result else None
        except sqlite3.Error as e:
            print(f"Error loading session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> None:
        """
        Delete session data from SQLite.
        
        Args:
            session_id (str): Unique session identifier
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

def get_storage_adapter() -> StorageAdapter:
    """
    Factory function to get the appropriate storage adapter.
    Currently returns SQLite adapter for local development.
    
    Returns:
        StorageAdapter: Configured storage adapter instance
    """
    return SQLiteAdapter()