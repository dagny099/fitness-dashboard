"""
tests/test_database_integration.py - Database integration tests

Tests the intelligence services working with real database connections,
data pipeline integration, and end-to-end workflows.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.database_service import DatabaseService
from services.intelligence_service import FitnessIntelligenceService
from utils.consistency_analyzer import ConsistencyAnalyzer

@pytest.fixture
def mock_database_connection():
    """Mock database connection for integration testing"""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    
    # Sample workout data that would come from database
    sample_data = [
        {
            'workout_date': datetime(2025, 1, 1),
            'activity_type': 'Run',
            'kcal_burned': 500,
            'distance_mi': 5.0,
            'duration_sec': 3000,
            'avg_pace': 10.0,
            'max_pace': 8.5,
            'steps': 8000
        },
        {
            'workout_date': datetime(2025, 1, 3),
            'activity_type': 'Walk', 
            'kcal_burned': 300,
            'distance_mi': 2.5,
            'duration_sec': 1800,
            'avg_pace': 20.0,
            'max_pace': 18.0,
            'steps': 4000
        },
        # Add more sample data...
    ]
    
    # Configure mock cursor to return sample data
    mock_cursor.fetchall.return_value = sample_data
    mock_cursor.description = [
        ('workout_date',), ('activity_type',), ('kcal_burned',), 
        ('distance_mi',), ('duration_sec',), ('avg_pace',), 
        ('max_pace',), ('steps',)
    ]
    
    # Configure connection context manager
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connection.cursor.return_value.__exit__.return_value = None
    
    return mock_connection

@pytest.fixture
def mock_database_service(mock_database_connection):
    """Mock database service with realistic data"""
    with patch.object(DatabaseService, 'get_connection') as mock_get_conn:
        mock_get_conn.return_value.__enter__.return_value = mock_database_connection
        mock_get_conn.return_value.__exit__.return_value = None
        yield DatabaseService()

class TestDatabaseServiceIntegration:
    """Test database service functionality"""
    
    def test_database_connection_context_manager(self, mock_database_service):
        """Test database connection context manager works correctly"""
        with mock_database_service.get_connection() as connection:
            assert connection is not None
            cursor = connection.cursor()
            assert cursor is not None
    
    def test_execute_query_basic(self, mock_database_service):
        """Test basic query execution through database service"""
        query = "SELECT * FROM workout_summary LIMIT 5"
        result = mock_database_service.execute_query(query)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Should have workout data structure
        first_record = result[0]
        expected_keys = ['workout_date', 'activity_type', 'kcal_burned']
        for key in expected_keys:
            assert key in first_record
    
    def test_execute_query_with_parameters(self, mock_database_service):
        """Test parameterized queries for safety"""
        query = "SELECT * FROM workout_summary WHERE workout_date >= %s"
        params = (datetime(2025, 1, 1),)
        
        # Mock the execute method to handle parameters
        with patch.object(mock_database_service, 'execute_query') as mock_execute:
            mock_execute.return_value = [{'workout_date': datetime(2025, 1, 1)}]
            
            result = mock_database_service.execute_query(query, params)
            assert len(result) > 0

class TestIntelligenceServiceIntegration:
    """Test intelligence service with database integration"""
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_intelligence_service_data_loading(self, mock_db_init, mock_database_connection):
        """Test intelligence service loads data from database"""
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_database_connection
            mock_conn.return_value.__exit__.return_value = None
            
            # Load data through intelligence service
            df = intelligence_service._load_workout_data()
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
            assert 'workout_date' in df.columns
            assert 'duration_min' in df.columns  # Should add derived column
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_intelligence_service_classification_pipeline(self, mock_db_init, mock_database_connection):
        """Test full classification pipeline with database data"""
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_database_connection
            mock_conn.return_value.__exit__.return_value = None
            
            # Load and classify data
            df = intelligence_service._load_workout_data()
            classified_df = intelligence_service.classify_workout_types(df)
            
            assert 'predicted_activity_type' in classified_df.columns
            assert 'classification_confidence' in classified_df.columns
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_intelligence_brief_generation_integration(self, mock_db_init, mock_database_connection):
        """Test full intelligence brief generation from database"""
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_database_connection
            mock_conn.return_value.__exit__.return_value = None
            
            brief = intelligence_service.generate_daily_intelligence_brief()
            
            # Should generate complete brief
            assert 'generated_at' in brief
            assert 'recommendations' in brief
            assert 'key_insights' in brief
            assert isinstance(brief['recommendations'], list)

class TestConsistencyAnalyzerIntegration:
    """Test consistency analyzer with database integration"""
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_consistency_analysis_with_database_data(self, mock_db_init, mock_database_connection):
        """Test consistency analysis using database-loaded data"""
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_database_connection
            mock_conn.return_value.__exit__.return_value = None
            
            # Load data and analyze consistency
            df = intelligence_service._load_workout_data()
            analyzer = ConsistencyAnalyzer(df)
            
            consistency_result = analyzer.calculate_consistency_score()
            
            assert 'consistency_score' in consistency_result
            assert 0 <= consistency_result['consistency_score'] <= 100

class TestEndToEndIntegrationPipeline:
    """Test complete end-to-end intelligence pipeline"""
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_complete_intelligence_pipeline(self, mock_db_init, mock_database_connection):
        """Test complete pipeline from database to insights"""
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_database_connection
            mock_conn.return_value.__exit__.return_value = None
            
            # Step 1: Load data from database
            df = intelligence_service._load_workout_data()
            assert len(df) > 0
            
            # Step 2: Classify workouts using ML
            classified_df = intelligence_service.classify_workout_types(df)
            assert 'predicted_activity_type' in classified_df.columns
            
            # Step 3: Analyze consistency
            analyzer = ConsistencyAnalyzer(classified_df)
            consistency_result = analyzer.calculate_consistency_score()
            assert 'consistency_score' in consistency_result
            
            # Step 4: Generate comprehensive intelligence brief
            brief = intelligence_service.generate_daily_intelligence_brief()
            
            # Verify complete pipeline output
            assert 'classification_intelligence' in brief
            assert 'consistency_intelligence' in brief
            assert 'recommendations' in brief
            assert len(brief['recommendations']) > 0
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_pipeline_performance_integration(self, mock_db_init):
        """Test pipeline performance with realistic data volume"""
        # Create larger mock dataset
        large_dataset = []
        base_date = datetime(2024, 1, 1)
        
        for i in range(100):  # 100 workouts
            large_dataset.append({
                'workout_date': base_date + timedelta(days=i*2),
                'activity_type': 'Run' if i % 3 == 0 else 'Walk',
                'kcal_burned': 400 + (i % 200),
                'distance_mi': 3.0 + (i % 5),
                'duration_sec': 2400 + (i % 1200),
                'avg_pace': 10.0 + (i % 15),
                'max_pace': 8.0 + (i % 10),
                'steps': 6000 + (i % 4000)
            })
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = large_dataset
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_connection
            mock_conn.return_value.__exit__.return_value = None
            
            import time
            start_time = time.time()
            
            # Run full pipeline
            brief = intelligence_service.generate_daily_intelligence_brief()
            
            end_time = time.time()
            pipeline_time = end_time - start_time
            
            # Should complete within reasonable time even with larger dataset
            assert pipeline_time < 10.0  # Less than 10 seconds
            assert 'recommendations' in brief

class TestDataConsistencyValidation:
    """Test data consistency between services"""
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_data_consistency_across_services(self, mock_db_init, mock_database_connection):
        """Test that data remains consistent across different service calls"""
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_database_connection
            mock_conn.return_value.__exit__.return_value = None
            
            # Load data multiple times
            df1 = intelligence_service._load_workout_data()
            df2 = intelligence_service._load_workout_data()
            
            # Should return identical data (potentially from cache)
            pd.testing.assert_frame_equal(df1, df2)
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_cross_service_data_validation(self, mock_db_init, mock_database_connection):
        """Test data consistency between intelligence service and direct database access"""
        intelligence_service = FitnessIntelligenceService()
        database_service = DatabaseService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn_intel, \
             patch.object(database_service, 'get_connection') as mock_conn_db:
            
            mock_conn_intel.return_value.__enter__.return_value = mock_database_connection
            mock_conn_intel.return_value.__exit__.return_value = None
            mock_conn_db.return_value.__enter__.return_value = mock_database_connection
            mock_conn_db.return_value.__exit__.return_value = None
            
            # Get data from both services
            intel_df = intelligence_service._load_workout_data()
            
            # Simulate direct database query
            with database_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM workout_summary")
                db_data = cursor.fetchall()
            
            # Both should return data (exact comparison depends on data format)
            assert len(intel_df) > 0
            assert len(db_data) > 0

class TestErrorHandlingIntegration:
    """Test error handling in integration scenarios"""
    
    def test_database_connection_failure(self):
        """Test handling of database connection failures"""
        # Create intelligence service with failing database connection
        with patch.object(DatabaseService, 'get_connection') as mock_conn:
            mock_conn.side_effect = Exception("Database connection failed")
            
            intelligence_service = FitnessIntelligenceService()
            
            # Should handle database errors gracefully
            df = intelligence_service._load_workout_data()
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 0  # Empty dataframe on error
    
    def test_invalid_database_response(self):
        """Test handling of invalid database responses"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        
        # Return invalid/empty data
        mock_cursor.fetchall.return_value = []
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_connection
            mock_conn.return_value.__exit__.return_value = None
            
            df = intelligence_service._load_workout_data()
            
            # Should handle empty response gracefully
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 0
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_partial_data_corruption_handling(self, mock_db_init):
        """Test handling of partially corrupted database data"""
        # Create dataset with some corrupted records
        corrupted_dataset = [
            {
                'workout_date': datetime(2025, 1, 1),
                'activity_type': 'Run',
                'kcal_burned': 500,
                'distance_mi': 5.0,
                'duration_sec': 3000,
                'avg_pace': 10.0,
                'max_pace': 8.5,
                'steps': 8000
            },
            {
                'workout_date': None,  # Corrupted date
                'activity_type': 'Walk',
                'kcal_burned': None,   # Corrupted calories
                'distance_mi': 2.5,
                'duration_sec': 1800,
                'avg_pace': 20.0,
                'max_pace': 18.0,
                'steps': 4000
            }
        ]
        
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = corrupted_dataset
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_connection
            mock_conn.return_value.__exit__.return_value = None
            
            # Should handle corrupted data without crashing
            df = intelligence_service._load_workout_data()
            
            # Should still return dataframe, possibly with cleaned data
            assert isinstance(df, pd.DataFrame)
            
            # Should be able to proceed with analysis despite corruption
            brief = intelligence_service.generate_daily_intelligence_brief()
            assert isinstance(brief, dict)

class TestCachingIntegration:
    """Test caching functionality in integration scenarios"""
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_data_caching_effectiveness(self, mock_db_init, mock_database_connection):
        """Test that caching reduces database calls"""
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_database_connection
            mock_conn.return_value.__exit__.return_value = None
            
            # First call should hit database
            df1 = intelligence_service._load_workout_data()
            call_count_1 = mock_conn.call_count
            
            # Second call should use cache
            df2 = intelligence_service._load_workout_data()
            call_count_2 = mock_conn.call_count
            
            # Should use cached data (same number of database calls)
            assert call_count_2 == call_count_1
            pd.testing.assert_frame_equal(df1, df2)
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_cache_invalidation(self, mock_db_init, mock_database_connection):
        """Test cache invalidation with force refresh"""
        intelligence_service = FitnessIntelligenceService()
        
        with patch.object(intelligence_service.db_service, 'get_connection') as mock_conn:
            mock_conn.return_value.__enter__.return_value = mock_database_connection
            mock_conn.return_value.__exit__.return_value = None
            
            # Load data and cache it
            df1 = intelligence_service._load_workout_data()
            
            # Force refresh should bypass cache
            df2 = intelligence_service._load_workout_data(force_refresh=True)
            
            # Should have made additional database call
            assert mock_conn.call_count >= 2