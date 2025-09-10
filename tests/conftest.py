"""
tests/conftest.py - Shared test configurations and fixtures
"""

# In tests/conftest.py

import pytest
import pandas as pd
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.database_service import DatabaseService
from utils.session_manager import SessionManager

@pytest.fixture
def test_database():
    """
    Sets up a test database with known data.
    """
    # Create test data
    test_data = {
        'workout_id': [1, 2, 3],
        'workout_date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'distance_mi': [3.1, 4.2, 5.0],
        'duration_sec': [1800, 2100, 2400],
        'kcal_burned': [300, 400, 500],
        'avg_pace': [8.5, 9.0, 8.8],
        'max_pace': [7.5, 8.0, 7.8]
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(test_data)
    
    # Here you could add code to populate a test database
    # For now, we'll just return the test data
    return df

@pytest.fixture
def mock_execute_query(test_database):
    """
    Creates a mock version of execute_query that uses our test data.
    """
    def mock_query(query, **kwargs):
        # Very simple query parser - just for testing
        if 'workout_summary' not in query:
            return None
        if 'WHERE' in query:
            # Parse WHERE clause (simplified)
            return test_database.head(1)
        return test_database
    
    return mock_query

@pytest.fixture
def clean_test_db():
    """
    This fixture provides a clean test database for each test.
    It's like resetting the gym equipment to its starting position
    before each new exercise.
    """
    test_db = "test_sessions.db"
    # Clean up any existing test database
    if os.path.exists(test_db):
        os.remove(test_db)
    yield test_db  # Provide the clean database to the test
    # Clean up after the test
    if os.path.exists(test_db):
        os.remove(test_db)


@pytest.fixture
def session_manager(clean_test_db):
    """
    This fixture provides a fresh SessionManager instance for each test.
    It's like getting a fresh workout tracking sheet for each exercise.
    """
    # Configure the session manager to use our test database
    return SessionManager()
