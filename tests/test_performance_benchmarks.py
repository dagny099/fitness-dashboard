"""
tests/test_performance_benchmarks.py - Performance benchmarking tests

Comprehensive performance testing for intelligence services to ensure
scalability and responsiveness under various load conditions.
"""

import pytest
import pandas as pd
import numpy as np
import time
import psutil
import threading
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from concurrent.futures import ThreadPoolExecutor
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.intelligence_service import FitnessIntelligenceService
from services.database_service import DatabaseService
from utils.consistency_analyzer import ConsistencyAnalyzer
from utils.statistics import TrendAnalysis, AnomalyDetection, PerformanceMetrics

# Performance thresholds
CLASSIFICATION_THRESHOLD_1K = 5.0    # seconds for 1K workouts
CLASSIFICATION_THRESHOLD_10K = 15.0  # seconds for 10K workouts
BRIEF_GENERATION_THRESHOLD = 3.0    # seconds for intelligence brief
MEMORY_LIMIT_MB = 500               # MB memory limit for large operations
CONCURRENT_USERS = 10               # concurrent user simulation

@pytest.fixture
def small_dataset():
    """Generate small dataset (100 workouts) for baseline testing"""
    return generate_workout_dataset(100)

@pytest.fixture
def medium_dataset():
    """Generate medium dataset (1,000 workouts) for load testing"""
    return generate_workout_dataset(1000)

@pytest.fixture
def large_dataset():
    """Generate large dataset (10,000 workouts) for stress testing"""
    return generate_workout_dataset(10000)

def generate_workout_dataset(size):
    """Generate realistic workout dataset of specified size"""
    np.random.seed(42)  # Reproducible datasets
    
    # Generate dates over reasonable time period
    if size <= 100:
        date_range = 200  # 200 days for small dataset
    elif size <= 1000:
        date_range = 2000  # ~5.5 years for medium dataset  
    else:
        date_range = 5000  # ~13.7 years for large dataset
    
    start_date = datetime(2010, 1, 1)
    possible_dates = [start_date + timedelta(days=i) for i in range(date_range)]
    
    # Randomly select workout dates (with some clustering for realism)
    workout_dates = np.random.choice(possible_dates, size=size, replace=False)
    workout_dates = sorted(workout_dates)
    
    data = []
    for date in workout_dates:
        # Create realistic workout patterns
        day_of_week = date.weekday()
        
        if np.random.random() < 0.3:  # 30% chance of "choco adventure" style
            workout = {
                'workout_date': date,
                'activity_type': 'Walk',
                'avg_pace': np.random.uniform(18, 28),
                'distance_mi': np.random.uniform(1.0, 4.0),
                'duration_sec': int(np.random.uniform(1200, 4800)),
                'kcal_burned': int(np.random.uniform(150, 400)),
                'max_pace': np.random.uniform(16, 25),
                'steps': int(np.random.uniform(2000, 8000))
            }
        else:  # "Real run" style
            workout = {
                'workout_date': date,
                'activity_type': 'Run',
                'avg_pace': np.random.uniform(7, 15),
                'distance_mi': np.random.uniform(2.0, 12.0),
                'duration_sec': int(np.random.uniform(1800, 7200)),
                'kcal_burned': int(np.random.uniform(300, 1000)),
                'max_pace': np.random.uniform(6, 13),
                'steps': int(np.random.uniform(4000, 15000))
            }
        
        data.append(workout)
    
    return pd.DataFrame(data)

def measure_performance(func, *args, **kwargs):
    """Measure execution time and memory usage of a function"""
    process = psutil.Process()
    
    # Get initial memory
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Measure execution time
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    # Get peak memory (approximate)
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_delta = final_memory - initial_memory
    
    return {
        'result': result,
        'execution_time': end_time - start_time,
        'memory_delta_mb': memory_delta,
        'peak_memory_mb': final_memory
    }

class TestWorkoutClassificationPerformance:
    """Performance tests for workout classification"""
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_classification_performance_small_dataset(self, mock_db_init, small_dataset):
        """Test classification performance with small dataset (baseline)"""
        intelligence_service = FitnessIntelligenceService()
        
        perf_result = measure_performance(
            intelligence_service.classify_workout_types,
            small_dataset
        )
        
        # Should be very fast with small dataset
        assert perf_result['execution_time'] < 2.0
        assert perf_result['memory_delta_mb'] < 50  # Low memory usage
        
        # Verify result quality
        classified_df = perf_result['result']
        assert len(classified_df) == len(small_dataset)
        assert 'predicted_activity_type' in classified_df.columns
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_classification_performance_medium_dataset(self, mock_db_init, medium_dataset):
        """Test classification performance with medium dataset"""
        intelligence_service = FitnessIntelligenceService()
        
        perf_result = measure_performance(
            intelligence_service.classify_workout_types,
            medium_dataset
        )
        
        # Should meet performance threshold for 1K workouts
        assert perf_result['execution_time'] < CLASSIFICATION_THRESHOLD_1K
        assert perf_result['memory_delta_mb'] < MEMORY_LIMIT_MB
        
        # Verify result quality
        classified_df = perf_result['result']
        assert len(classified_df) == len(medium_dataset)
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_classification_performance_large_dataset(self, mock_db_init, large_dataset):
        """Test classification performance with large dataset (stress test)"""
        intelligence_service = FitnessIntelligenceService()
        
        perf_result = measure_performance(
            intelligence_service.classify_workout_types,
            large_dataset
        )
        
        # Should meet performance threshold for 10K workouts  
        assert perf_result['execution_time'] < CLASSIFICATION_THRESHOLD_10K
        assert perf_result['memory_delta_mb'] < MEMORY_LIMIT_MB
        
        # Verify result quality is maintained at scale
        classified_df = perf_result['result']
        assert len(classified_df) == len(large_dataset)
        
        # Classification rate should remain high even with large data
        classified_count = len(classified_df[classified_df['predicted_activity_type'] != 'unknown'])
        classification_rate = classified_count / len(classified_df) * 100
        assert classification_rate > 70  # Should classify >70% of workouts
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_classification_caching_performance(self, mock_db_init, medium_dataset):
        """Test performance improvement from caching"""
        intelligence_service = FitnessIntelligenceService()
        
        # First classification (cold cache)
        perf_result_1 = measure_performance(
            intelligence_service.classify_workout_types,
            medium_dataset
        )
        
        # Second classification (should use cache)
        perf_result_2 = measure_performance(
            intelligence_service.classify_workout_types,
            medium_dataset
        )
        
        # Cached version should be significantly faster
        speedup_factor = perf_result_1['execution_time'] / perf_result_2['execution_time']
        assert speedup_factor > 2  # Should be at least 2x faster with cache

class TestIntelligenceBriefPerformance:
    """Performance tests for intelligence brief generation"""
    
    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_brief_generation_performance(self, mock_load_data, medium_dataset):
        """Test intelligence brief generation performance"""
        mock_load_data.return_value = medium_dataset
        
        intelligence_service = FitnessIntelligenceService()
        
        perf_result = measure_performance(
            intelligence_service.generate_daily_intelligence_brief
        )
        
        # Should meet brief generation threshold
        assert perf_result['execution_time'] < BRIEF_GENERATION_THRESHOLD
        assert perf_result['memory_delta_mb'] < MEMORY_LIMIT_MB / 2  # Lower memory for brief
        
        # Verify brief quality
        brief = perf_result['result']
        assert 'recommendations' in brief
        assert 'key_insights' in brief
        assert len(brief['recommendations']) > 0
    
    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_specific_metric_analysis_performance(self, mock_load_data, large_dataset):
        """Test performance of specific metric deep-dive analysis"""
        mock_load_data.return_value = large_dataset
        
        intelligence_service = FitnessIntelligenceService()
        
        # Test analysis of different metrics
        metrics_to_test = ['kcal_burned', 'distance_mi', 'duration_sec']
        
        for metric in metrics_to_test:
            perf_result = measure_performance(
                intelligence_service.analyze_specific_metric,
                metric, 90  # 90-day analysis
            )
            
            # Each metric analysis should be fast
            assert perf_result['execution_time'] < 5.0
            
            # Verify analysis quality
            analysis = perf_result['result']
            if 'error' not in analysis:
                assert 'trend_analysis' in analysis
                assert 'insights' in analysis

class TestConsistencyAnalysisPerformance:
    """Performance tests for consistency analysis"""
    
    def test_consistency_scoring_performance(self, large_dataset):
        """Test consistency scoring performance with large dataset"""
        analyzer = ConsistencyAnalyzer(large_dataset)
        
        perf_result = measure_performance(
            analyzer.calculate_consistency_score
        )
        
        # Should complete quickly even with large dataset
        assert perf_result['execution_time'] < 8.0
        assert perf_result['memory_delta_mb'] < MEMORY_LIMIT_MB / 4
        
        # Verify result quality
        result = perf_result['result']
        assert 'consistency_score' in result
        assert 0 <= result['consistency_score'] <= 100
    
    def test_pattern_analysis_performance(self, large_dataset):
        """Test workout pattern analysis performance"""
        analyzer = ConsistencyAnalyzer(large_dataset)
        
        perf_result = measure_performance(
            analyzer.analyze_workout_patterns
        )
        
        # Pattern analysis should be efficient
        assert perf_result['execution_time'] < 5.0
        
        # Verify patterns are discovered
        patterns = perf_result['result']
        assert 'preferred_days' in patterns
        assert 'frequency_analysis' in patterns
    
    def test_phase_detection_performance(self, large_dataset):
        """Test consistency phase detection performance"""
        analyzer = ConsistencyAnalyzer(large_dataset)
        
        perf_result = measure_performance(
            analyzer.detect_consistency_phases
        )
        
        # Phase detection can be more intensive but should still be reasonable
        assert perf_result['execution_time'] < 10.0
        
        # Verify phases are detected
        phases = perf_result['result']
        assert isinstance(phases, list)

class TestStatisticalAnalysisPerformance:
    """Performance tests for statistical utilities"""
    
    def test_trend_analysis_performance(self, large_dataset):
        """Test trend analysis performance on large time series"""
        calories_data = large_dataset['kcal_burned'].dropna()
        
        perf_result = measure_performance(
            TrendAnalysis.calculate_trend,
            calories_data
        )
        
        # Trend analysis should be very fast
        assert perf_result['execution_time'] < 1.0
        
        # Verify trend is calculated
        trend_result = perf_result['result']
        assert 'trend_direction' in trend_result
        assert 'confidence' in trend_result
    
    def test_anomaly_detection_performance(self, large_dataset):
        """Test anomaly detection performance"""
        distance_data = large_dataset['distance_mi'].dropna()
        
        # Test different anomaly detection methods
        methods = ['iqr', 'zscore', 'modified_zscore']
        
        for method in methods:
            perf_result = measure_performance(
                AnomalyDetection.detect_outliers,
                distance_data, method
            )
            
            # Anomaly detection should be fast
            assert perf_result['execution_time'] < 2.0
            
            # Verify anomalies are detected
            anomaly_result = perf_result['result']
            assert 'total_outliers' in anomaly_result
    
    def test_forecasting_performance(self, medium_dataset):
        """Test forecasting performance"""
        pace_data = medium_dataset['avg_pace'].dropna()
        
        perf_result = measure_performance(
            TrendAnalysis.forecast_values,
            pace_data, 30  # 30-day forecast
        )
        
        # Forecasting should be quick
        assert perf_result['execution_time'] < 2.0
        
        # Verify forecast is generated
        forecast_result = perf_result['result']
        assert len(forecast_result['forecast']) == 30

class TestConcurrentUserPerformance:
    """Test performance under concurrent user load"""
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_concurrent_classification_requests(self, mock_db_init, medium_dataset):
        """Test multiple concurrent classification requests"""
        
        def classify_workouts():
            intelligence_service = FitnessIntelligenceService()
            return intelligence_service.classify_workout_types(medium_dataset)
        
        # Simulate concurrent users
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
            futures = [executor.submit(classify_workouts) for _ in range(CONCURRENT_USERS)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle concurrent load reasonably well
        assert total_time < CLASSIFICATION_THRESHOLD_1K * 3  # Allow 3x time for concurrency
        
        # All results should be valid
        for result in results:
            assert len(result) == len(medium_dataset)
            assert 'predicted_activity_type' in result.columns
    
    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_concurrent_brief_generation(self, mock_load_data, medium_dataset):
        """Test concurrent intelligence brief generation"""
        mock_load_data.return_value = medium_dataset
        
        def generate_brief():
            intelligence_service = FitnessIntelligenceService()
            return intelligence_service.generate_daily_intelligence_brief()
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
            futures = [executor.submit(generate_brief) for _ in range(CONCURRENT_USERS)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle concurrent brief generation
        assert total_time < BRIEF_GENERATION_THRESHOLD * 5  # Allow 5x time for concurrency
        
        # All briefs should be valid
        for brief in results:
            assert 'recommendations' in brief
            assert 'key_insights' in brief

class TestMemoryEfficiency:
    """Test memory efficiency and leak detection"""
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_memory_leak_detection(self, mock_db_init, medium_dataset):
        """Test for memory leaks in repeated operations"""
        intelligence_service = FitnessIntelligenceService()
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform multiple classification operations
        for i in range(10):
            classified_df = intelligence_service.classify_workout_types(medium_dataset)
            
            # Force garbage collection periodically
            if i % 3 == 0:
                import gc
                gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be minimal (< 100MB for 10 operations)
        assert memory_growth < 100
    
    def test_large_dataset_memory_efficiency(self, large_dataset):
        """Test memory efficiency with large datasets"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        analyzer = ConsistencyAnalyzer(large_dataset)
        consistency_result = analyzer.calculate_consistency_score()
        patterns = analyzer.analyze_workout_patterns()
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = peak_memory - initial_memory
        
        # Should stay within memory limits even with large dataset
        assert memory_usage < MEMORY_LIMIT_MB
        
        # Results should still be valid
        assert 'consistency_score' in consistency_result
        assert 'preferred_days' in patterns

class TestPerformanceRegression:
    """Test for performance regression detection"""
    
    performance_baselines = {
        'small_dataset_classification': 2.0,    # seconds
        'medium_dataset_classification': 5.0,   # seconds
        'brief_generation': 3.0,                # seconds
        'consistency_analysis': 8.0,            # seconds
        'memory_usage_mb': 500                  # MB
    }
    
    @patch.object(DatabaseService, '__init__', return_value=None)
    def test_performance_baseline_classification(self, mock_db_init, small_dataset, medium_dataset):
        """Test that classification performance hasn't regressed"""
        intelligence_service = FitnessIntelligenceService()
        
        # Test small dataset
        start_time = time.time()
        intelligence_service.classify_workout_types(small_dataset)
        small_time = time.time() - start_time
        
        # Test medium dataset  
        start_time = time.time()
        intelligence_service.classify_workout_types(medium_dataset)
        medium_time = time.time() - start_time
        
        # Should meet baseline performance
        assert small_time < self.performance_baselines['small_dataset_classification']
        assert medium_time < self.performance_baselines['medium_dataset_classification']
    
    @patch.object(FitnessIntelligenceService, '_load_workout_data')
    def test_performance_baseline_brief_generation(self, mock_load_data, medium_dataset):
        """Test that brief generation performance hasn't regressed"""
        mock_load_data.return_value = medium_dataset
        intelligence_service = FitnessIntelligenceService()
        
        start_time = time.time()
        intelligence_service.generate_daily_intelligence_brief()
        brief_time = time.time() - start_time
        
        assert brief_time < self.performance_baselines['brief_generation']

class TestScalabilityLimits:
    """Test scalability limits and breaking points"""
    
    @pytest.mark.slow
    def test_maximum_dataset_size(self):
        """Test with extremely large dataset to find limits"""
        # Generate very large dataset (50K workouts) - marked as slow test
        very_large_dataset = generate_workout_dataset(50000)
        
        intelligence_service = FitnessIntelligenceService()
        
        # This might fail or be very slow - that's expected for limit testing
        try:
            start_time = time.time()
            classified_df = intelligence_service.classify_workout_types(very_large_dataset)
            execution_time = time.time() - start_time
            
            # If it succeeds, it should still complete within reasonable time
            assert execution_time < 60.0  # 1 minute max
            assert len(classified_df) == len(very_large_dataset)
            
        except MemoryError:
            # Expected to potentially fail with memory error
            pytest.skip("Dataset too large for current system - this defines our limit")
        except Exception as e:
            # Log the failure point for analysis
            pytest.fail(f"Failed at 50K workouts with error: {str(e)}")

# Utility functions for performance monitoring
def profile_function_performance(func, *args, **kwargs):
    """Comprehensive performance profiling of a function"""
    import cProfile
    import pstats
    from io import StringIO
    
    # Profile the function
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    
    # Get profiling stats
    stats_buffer = StringIO()
    stats = pstats.Stats(profiler, stream=stats_buffer)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
    
    return {
        'result': result,
        'profile_output': stats_buffer.getvalue()
    }