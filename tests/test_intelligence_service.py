"""
tests/test_intelligence_service.py - Core tests for FitnessIntelligenceService

Tests the heart of the AI system: workout classification, intelligence briefs,
performance analysis, and recommendation generation.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.intelligence_service import FitnessIntelligenceService
from services.database_service import DatabaseService

@pytest.fixture
def sample_workout_data():
    """Generate realistic workout data for testing"""
    np.random.seed(42)  # Reproducible results
    
    # Create 30 days of varied workout data
    dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
    data = []
    
    for i, date in enumerate(dates):
        # Create different workout patterns
        if i % 7 in [0, 6]:  # Weekends - longer, slower "choco adventures"
            workout = {
                'workout_date': date,
                'activity_type': 'Walk',
                'avg_pace': np.random.uniform(20, 25),  # Slow walking pace
                'distance_mi': np.random.uniform(1.5, 3.0),
                'duration_sec': int(np.random.uniform(1800, 3600)),  # 30-60 min
                'kcal_burned': int(np.random.uniform(200, 400)),
                'max_pace': np.random.uniform(18, 23),
                'steps': int(np.random.uniform(3000, 6000))
            }
        elif i % 7 in [1, 3, 5]:  # Weekdays - faster "real runs"
            workout = {
                'workout_date': date,
                'activity_type': 'Run',
                'avg_pace': np.random.uniform(8, 12),  # Running pace
                'distance_mi': np.random.uniform(3.0, 6.0),
                'duration_sec': int(np.random.uniform(1800, 4800)),  # 30-80 min
                'kcal_burned': int(np.random.uniform(400, 800)),
                'max_pace': np.random.uniform(7, 10),
                'steps': int(np.random.uniform(6000, 12000))
            }
        else:  # Some days off
            continue
            
        data.append(workout)
    
    return pd.DataFrame(data)

@pytest.fixture
def intelligence_service():
    """Create intelligence service with mocked database"""
    with patch.object(DatabaseService, '__init__', return_value=None):
        service = FitnessIntelligenceService()
        return service

@pytest.fixture
def mock_database_service(sample_workout_data):
    """Mock database service returning sample data"""
    mock_service = Mock()
    
    # Mock the execute_query method to return sample data
    mock_service.execute_query.return_value = sample_workout_data.to_dict('records')
    
    # Mock connection context manager
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = sample_workout_data.to_dict('records')
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_service.get_connection.return_value.__enter__.return_value = mock_connection
    
    return mock_service

class TestWorkoutClassification:
    """Test ML-based workout classification functionality"""
    
    def test_classify_workout_types_basic(self, intelligence_service, sample_workout_data):
        """Test that workout classification runs and produces expected output"""
        result_df = intelligence_service.classify_workout_types(sample_workout_data)
        
        # Should have same number of rows
        assert len(result_df) == len(sample_workout_data)
        
        # Should add classification columns
        assert 'predicted_activity_type' in result_df.columns
        assert 'classification_confidence' in result_df.columns
        
        # Classifications should be valid types
        valid_types = ['real_run', 'choco_adventure', 'mixed', 'outlier', 'unknown']
        assert all(result_df['predicted_activity_type'].isin(valid_types))
        
        # Confidence scores should be valid (0-1)
        assert all(result_df['classification_confidence'].between(0, 1, inclusive='both'))

    def test_classify_workout_types_patterns(self, intelligence_service, sample_workout_data):
        """Test that classification correctly identifies workout patterns"""
        result_df = intelligence_service.classify_workout_types(sample_workout_data)
        
        # Slow, short workouts should be classified as choco_adventure
        slow_workouts = result_df[result_df['avg_pace'] > 18]
        choco_classifications = slow_workouts['predicted_activity_type'] == 'choco_adventure'
        assert choco_classifications.sum() > 0  # Should find some choco adventures
        
        # Fast, longer workouts should be classified as real_run  
        fast_workouts = result_df[result_df['avg_pace'] < 15]
        run_classifications = fast_workouts['predicted_activity_type'] == 'real_run'
        assert run_classifications.sum() > 0  # Should find some real runs

    def test_classify_empty_dataframe(self, intelligence_service):
        """Test classification handles empty data gracefully"""
        empty_df = pd.DataFrame()
        result = intelligence_service.classify_workout_types(empty_df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_classify_insufficient_data(self, intelligence_service):
        """Test classification with insufficient data for clustering"""
        minimal_data = pd.DataFrame({
            'avg_pace': [10.0, 11.0],
            'distance_mi': [3.0, 3.5],
            'duration_sec': [1800, 2100]
        })
        
        result = intelligence_service.classify_workout_types(minimal_data)
        
        # Should return with unknown classifications
        assert all(result['predicted_activity_type'] == 'unknown')
        assert all(result['classification_confidence'] == 0.0)

class TestIntelligenceBriefGeneration:
    """Test daily intelligence brief generation"""
    
    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_generate_daily_intelligence_brief_structure(self, mock_load_data, intelligence_service, sample_workout_data):
        """Test that intelligence brief has expected structure"""
        mock_load_data.return_value = sample_workout_data
        
        brief = intelligence_service.generate_daily_intelligence_brief()
        
        # Should have core sections
        expected_sections = [
            'generated_at', 'analysis_period', 'total_workouts_analyzed',
            'classification_intelligence', 'performance_intelligence', 
            'consistency_intelligence', 'anomaly_intelligence',
            'predictive_intelligence', 'recommendations', 'key_insights'
        ]
        
        for section in expected_sections:
            assert section in brief

    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_generate_recommendations(self, mock_load_data, intelligence_service, sample_workout_data):
        """Test AI recommendation generation"""
        mock_load_data.return_value = sample_workout_data
        
        brief = intelligence_service.generate_daily_intelligence_brief()
        recommendations = brief['recommendations']
        
        # Should generate at least one recommendation
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert len(recommendations) <= 4  # Limited to top 4
        
        # Each recommendation should be a string with emoji
        for rec in recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 10  # Should be descriptive

    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_generate_key_insights(self, mock_load_data, intelligence_service, sample_workout_data):
        """Test key insights generation"""
        mock_load_data.return_value = sample_workout_data
        
        brief = intelligence_service.generate_daily_intelligence_brief()
        insights = brief['key_insights']
        
        # Should generate insights
        assert isinstance(insights, list)
        assert len(insights) > 0
        assert len(insights) <= 4  # Limited to top 4
        
        # Each insight should be informative
        for insight in insights:
            assert isinstance(insight, str)
            assert len(insight) > 10

class TestPerformanceAnalysis:
    """Test performance metrics and analysis"""
    
    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_analyze_specific_metric_calories(self, mock_load_data, intelligence_service, sample_workout_data):
        """Test deep dive analysis of calorie metric"""
        mock_load_data.return_value = sample_workout_data
        
        analysis = intelligence_service.analyze_specific_metric('kcal_burned')
        
        # Should have comprehensive analysis structure
        expected_keys = [
            'metric', 'analysis_period', 'data_points', 'basic_stats',
            'trend_analysis', 'forecast', 'anomaly_analysis', 
            'improvement_analysis', 'plateau_analysis', 'insights'
        ]
        
        for key in expected_keys:
            assert key in analysis

        # Basic stats should be reasonable
        stats = analysis['basic_stats']
        assert stats['mean'] > 0
        assert stats['min'] >= 0
        assert stats['max'] > stats['mean']

    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_analyze_nonexistent_metric(self, mock_load_data, intelligence_service, sample_workout_data):
        """Test analysis of metric that doesn't exist"""
        mock_load_data.return_value = sample_workout_data
        
        analysis = intelligence_service.analyze_specific_metric('nonexistent_metric')
        
        assert 'error' in analysis
        assert 'not available' in analysis['error']

    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_get_performance_summary(self, mock_load_data, intelligence_service, sample_workout_data):
        """Test performance summary generation"""
        mock_load_data.return_value = sample_workout_data
        
        summary = intelligence_service.get_performance_summary('30d')
        
        # Should have summary structure
        expected_keys = ['timeframe', 'total_workouts', 'workout_frequency', 'metrics', 'intelligence_score']
        for key in expected_keys:
            assert key in summary
        
        # Metrics should be reasonable
        assert summary['total_workouts'] > 0
        assert summary['workout_frequency'] > 0

class TestClassificationSummary:
    """Test classification summary and statistics"""
    
    def test_get_classification_summary(self, intelligence_service, sample_workout_data):
        """Test classification summary generation"""
        # First classify the data
        classified_df = intelligence_service.classify_workout_types(sample_workout_data)
        
        # Get summary
        summary = intelligence_service.get_classification_summary(classified_df)
        
        # Should have summary structure
        expected_keys = ['classification_distribution', 'classification_rate', 'confidence_by_type']
        for key in expected_keys:
            assert key in summary
        
        # Classification rate should be reasonable (most workouts classified)
        assert summary['classification_rate'] >= 70  # At least 70% classified

    def test_get_classification_summary_no_data(self, intelligence_service):
        """Test classification summary with no classification data"""
        df_without_classification = pd.DataFrame({'workout_date': [datetime.now()]})
        
        summary = intelligence_service.get_classification_summary(df_without_classification)
        assert 'error' in summary

class TestDataCaching:
    """Test data caching functionality"""
    
    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_classification_caching(self, mock_load_data, intelligence_service, sample_workout_data):
        """Test that classification results are cached"""
        mock_load_data.return_value = sample_workout_data
        
        # First call
        result1 = intelligence_service.classify_workout_types(sample_workout_data)
        
        # Second call with same data should use cache
        result2 = intelligence_service.classify_workout_types(sample_workout_data)
        
        # Results should be identical (from cache)
        pd.testing.assert_frame_equal(result1, result2)

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_data_handling(self, intelligence_service):
        """Test handling of invalid workout data"""
        # Data with NaN values
        invalid_data = pd.DataFrame({
            'avg_pace': [10.0, np.nan, 12.0],
            'distance_mi': [3.0, 4.0, np.nan],
            'duration_sec': [1800, 2100, 2400]
        })
        
        # Should not crash
        result = intelligence_service.classify_workout_types(invalid_data)
        assert isinstance(result, pd.DataFrame)

    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_database_error_handling(self, mock_load_data, intelligence_service):
        """Test handling of database errors"""
        # Simulate database error
        mock_load_data.return_value = pd.DataFrame()
        
        brief = intelligence_service.generate_daily_intelligence_brief()
        assert 'error' in brief

class TestPerformanceBenchmarks:
    """Performance benchmarks for intelligence operations"""
    
    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_classification_speed(self, mock_load_data, intelligence_service):
        """Test classification performance with larger datasets"""
        # Generate larger dataset (1000 workouts)
        large_dataset = pd.DataFrame({
            'avg_pace': np.random.uniform(8, 25, 1000),
            'distance_mi': np.random.uniform(1, 10, 1000),
            'duration_sec': np.random.uniform(1200, 7200, 1000)
        })
        mock_load_data.return_value = large_dataset
        
        import time
        start_time = time.time()
        
        result = intelligence_service.classify_workout_types(large_dataset)
        
        end_time = time.time()
        classification_time = end_time - start_time
        
        # Should complete within reasonable time (5 seconds)
        assert classification_time < 5.0
        assert len(result) == 1000

    @patch.object(FitnessIntelligenceService, '_load_workout_data')  
    def test_intelligence_brief_speed(self, mock_load_data, intelligence_service, sample_workout_data):
        """Test intelligence brief generation speed"""
        mock_load_data.return_value = sample_workout_data
        
        import time
        start_time = time.time()
        
        brief = intelligence_service.generate_daily_intelligence_brief()
        
        end_time = time.time()
        brief_time = end_time - start_time
        
        # Should complete within reasonable time (3 seconds)
        assert brief_time < 3.0
        assert 'recommendations' in brief