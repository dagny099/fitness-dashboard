"""
session_manager.py

This module provides session state management for the SQL Practice Dashboard.
It handles persistence of notes, query history, and saved queries.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import uuid
from storage import get_storage_adapter

class SessionManager:
    """
    Manages session state for the dashboard including scratchpad, query history,
    and saved queries. Integrates with a storage backend for persistence.
    
    Attributes:
        storage: StorageAdapter instance for data persistence
    """
    
    def __init__(self):
        """
        Initialize session state and storage.
        Creates a new session ID if one doesn't exist and initializes all
        required session state variables.
        """
        # Initialize storage
        self.storage = get_storage_adapter()
        
        # Initialize or restore session state
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            self._init_session_state()
        else:
            self._restore_session_state()
    
    def _init_session_state(self) -> None:
        """Initialize empty session state with default values."""
        if 'scratchpad' not in st.session_state:
            st.session_state.scratchpad = ""
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        if 'saved_queries' not in st.session_state:
            st.session_state.saved_queries = []
    
    def _restore_session_state(self) -> None:
        """
        Restore session state from storage.
        If stored data exists, it will be loaded into session state.
        """
        stored_data = self.storage.load_session(st.session_state.session_id)
        if stored_data:
            st.session_state.scratchpad = stored_data.get('scratchpad', '')
            st.session_state.query_history = stored_data.get('query_history', [])
            st.session_state.saved_queries = stored_data.get('saved_queries', [])
    
    def _save_session_state(self) -> None:
        """
        Save current session state to storage.
        Includes scratchpad content, query history, and saved queries.
        """
        session_data = {
            'scratchpad': st.session_state.scratchpad,
            'query_history': st.session_state.query_history,
            'saved_queries': st.session_state.saved_queries
        }
        self.storage.save_session(st.session_state.session_id, session_data)
    
    def update_scratchpad(self, content: str) -> None:
        """
        Update scratchpad content and persist to storage.
        
        Args:
            content (str): The new content for the scratchpad
        """
        st.session_state.scratchpad = content
        self._save_session_state()
    
    def add_query_to_history(self, query: str, result: Optional[Dict] = None) -> None:
        """
        Add a query and its results to the session history.
        
        Args:
            query (str): The SQL query that was executed
            result (Optional[Dict]): Dictionary containing query results and metadata.
                Expected format:
                {
                    'columns': List[str],  # Column names
                    'row_count': int,      # Number of rows returned
                    'execution_time': float,# Query execution time in seconds
                    'error': str           # Error message if query failed
                }
        """
        query_record = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'result': result or {}
        }
        st.session_state.query_history.append(query_record)
        self._save_session_state()
    
    def add_saved_query(self, query: str, name: str = None, description: str = None) -> None:
        """
        Add a query to saved queries.
        
        Args:
            query (str): The SQL query to save
            name (str, optional): Custom name for the query
            description (str, optional): Description of what the query does
        """
        if 'saved_queries' not in st.session_state:
            st.session_state.saved_queries = []
            
        saved_query = {
            'name': name or f"Saved Query {len(st.session_state.saved_queries) + 1}",
            'query': query,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.saved_queries.append(saved_query)
        self._save_session_state()
    
    def get_scratchpad(self) -> str:
        """
        Retrieve current scratchpad content.
        
        Returns:
            str: Current scratchpad content
        """
        return st.session_state.scratchpad
    
    def get_query_history(self) -> List[Dict]:
        """
        Retrieve the complete query execution history.
        
        Returns:
            List[Dict]: List of query records with metadata
        """
        return st.session_state.query_history
    
    def get_saved_queries(self) -> List[Dict]:
        """
        Retrieve all saved queries.
        
        Returns:
            List[Dict]: List of saved queries with metadata
        """
        if 'saved_queries' not in st.session_state:
            st.session_state.saved_queries = []
        return st.session_state.saved_queries
    
    def delete_saved_query(self, index: int) -> None:
        """
        Delete a saved query by its index.
        
        Args:
            index (int): Index of the query to delete
        """
        if 'saved_queries' in st.session_state and 0 <= index < len(st.session_state.saved_queries):
            st.session_state.saved_queries.pop(index)
            self._save_session_state()
    
    def clear_history(self) -> None:
        """Clear query history and persist the change."""
        st.session_state.query_history = []
        self._save_session_state()
    
    def export_session(self, filepath: str) -> None:
        """
        Export session data to a JSON file.
        
        Args:
            filepath (str): Path where the JSON file should be saved
        """
        session_data = {
            'scratchpad': self.get_scratchpad(),
            'query_history': self.get_query_history(),
            'saved_queries': self.get_saved_queries()
        }
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)