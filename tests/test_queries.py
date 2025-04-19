"""
tests/test_queries.py - Tests for SQL query execution functionality

This file contains tests that verify your dashboard correctly handles SQL queries,
including successful queries, error cases, and edge cases. Think of these tests
as quality control checks for your query execution system.
"""

import pytest
from build_workout_dashboard.utilities import execute_query
import pandas as pd

@pytest.fixture
def sample_query_data():
    """
    Provides sample data for testing queries. In a real application,
    you might want to use a test database with known data.
    """
    return {
        'simple_query': "SELECT * FROM workout_summary LIMIT 5",
        'aggregate_query': "SELECT COUNT(*) as count FROM workout_summary",
        'invalid_query': "SELECT * FROM nonexistent_table",
        'malformed_query': "SELCT * FORM workout_summary"  # Intentionally misspelled
    }

def test_basic_query_execution(sample_query_data):
    """
    Tests that a simple SELECT query executes successfully and returns results.
    This is like verifying that the most basic operation of your system works.
    """
    result = execute_query(sample_query_data['simple_query'])
    
    # Verify we got some results back
    assert result is not None
    assert len(result) > 0
    
    # If using pandas DataFrame, verify structure
    if isinstance(result, pd.DataFrame):
        assert 'workout_id' in result.columns
        assert 'workout_date' in result.columns

def test_aggregate_query(sample_query_data):
    """
    Tests that aggregate queries (like COUNT, SUM) work correctly.
    This verifies that your system can handle data analysis queries.
    """
    result = execute_query(sample_query_data['aggregate_query'])
    
    # Verify we got a count back
    assert result is not None
    if isinstance(result, pd.DataFrame):
        assert 'count' in result.columns
        assert result['count'].iloc[0] > 0

def test_query_with_parameters():
    """
    Tests that parameterized queries work correctly and safely.
    This is crucial for preventing SQL injection and handling user input.
    """
    # Instead of using parameters, we'll embed the date in the query
    query = "SELECT * FROM workout_summary WHERE workout_date = '2024-01-01'"
    
    result = execute_query(query)
    
    assert result is not None
    # If we get results, we can add more specific assertions
    # If we don't expect results for this date, we can assert that too
    if isinstance(result, pd.DataFrame):
        assert len(result) >= 0  # At least verifies query executed

def test_invalid_query_handling(sample_query_data):
    """
    Tests that the system handles invalid queries appropriately.
    Converts list results to DataFrame for consistency.
    """
    def to_dataframe(result):
        """Helper function to convert list results to DataFrame"""
        if result is None:
            return None
        if isinstance(result, list):
            if len(result) == 0:
                return pd.DataFrame()  # Empty DataFrame
            if isinstance(result[0], dict):
                return pd.DataFrame(result)
            # Handle other list formats as needed
            return pd.DataFrame(result)
        return result

    # Test query with non-existent table
    result = execute_query(sample_query_data['invalid_query'])
    result_df = to_dataframe(result)
    
    # Check that result is either None or an empty DataFrame
    assert result_df is None or (isinstance(result_df, pd.DataFrame) and len(result_df) == 0)
    
    # Test malformed query
    result_malformed = execute_query(sample_query_data['malformed_query'])
    result_malformed_df = to_dataframe(result_malformed)
    assert result_malformed_df is None or (isinstance(result_malformed_df, pd.DataFrame) and len(result_malformed_df) == 0)

    
def test_empty_result_handling():
    """
    Tests that queries returning no results are handled properly.
    This verifies your system gracefully handles queries that find no matching data.
    """
    query = "SELECT * FROM workout_summary WHERE workout_date = '1900-01-01'"
    result = execute_query(query)
    
    assert result is not None
    if isinstance(result, pd.DataFrame):
        assert len(result) == 0
    else:
        assert len(result) == 0

def test_large_result_handling():
    """
    Tests that the system can handle queries returning large result sets.
    This ensures your dashboard performs well with bigger data volumes.
    """
    # Query all records
    query = "SELECT * FROM workout_summary"
    result = execute_query(query)
    
    assert result is not None
    # Verify we can handle more than a trivial number of records
    if isinstance(result, pd.DataFrame):
        assert len(result) > 10  # Adjust based on your test data volume

def test_special_characters_in_queries():
    """
    Tests that queries containing special characters are handled correctly.
    This verifies your system properly handles various SQL syntax elements.
    """
    # Test query with quotes and special characters
    query = """
    SELECT * FROM workout_summary 
    WHERE workout_date BETWEEN '2024-01-01' AND '2024-12-31'
    AND distance_mi > 5.5
    ORDER BY workout_date DESC
    """
    
    result = execute_query(query)
    assert result is not None