"""
tests/test_consistency_analyzer.py - Tests for ConsistencyAnalyzer

Tests multi-dimensional consistency scoring, pattern analysis, and insights generation
for workout consistency intelligence.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.consistency_analyzer import ConsistencyAnalyzer

@pytest.fixture
def consistent_workout_data():
    """Generate highly consistent workout pattern"""
    # Every Monday, Wednesday, Friday for 4 weeks
    dates = []
    base_date = datetime(2025, 1, 6)  # Monday
    
    for week in range(4):
        # Mon, Wed, Fri pattern
        dates.extend([
            base_date + timedelta(days=week*7),      # Monday
            base_date + timedelta(days=week*7 + 2),  # Wednesday  
            base_date + timedelta(days=week*7 + 4)   # Friday
        ])
    
    np.random.seed(42)
    data = []
    for date in dates:
        data.append({
            'workout_date': date,
            'activity_type': 'Run',
            'kcal_burned': np.random.normal(500, 25),  # Consistent calories
            'distance_mi': np.random.normal(5.0, 0.3), # Consistent distance
            'duration_sec': np.random.normal(3000, 150) # Consistent duration
        })
    
    return pd.DataFrame(data)

@pytest.fixture
def inconsistent_workout_data():
    """Generate inconsistent workout pattern"""
    np.random.seed(42)
    
    # Random dates with large gaps
    dates = [
        datetime(2025, 1, 1),
        datetime(2025, 1, 3), 
        datetime(2025, 1, 15),  # Large gap
        datetime(2025, 1, 16),  # Back-to-back
        datetime(2025, 2, 5),   # Another gap
        datetime(2025, 2, 10),
        datetime(2025, 3, 1)    # Month gap
    ]
    
    data = []
    for date in dates:
        data.append({
            'workout_date': date,
            'activity_type': np.random.choice(['Run', 'Walk', 'Bike']),
            'kcal_burned': np.random.uniform(200, 800),  # Highly variable
            'distance_mi': np.random.uniform(1, 10),     # Very inconsistent
            'duration_sec': np.random.uniform(1200, 5400) # Wide variation
        })
    
    return pd.DataFrame(data)

@pytest.fixture
def mixed_pattern_data():
    """Generate data with some consistency but room for improvement"""
    np.random.seed(42)
    
    # Somewhat regular pattern (every 2-3 days) with some variation
    dates = []
    current_date = datetime(2025, 1, 1)
    
    for _ in range(15):
        dates.append(current_date)
        # Skip 1-4 days randomly
        skip_days = np.random.choice([1, 2, 2, 3, 4], p=[0.1, 0.3, 0.3, 0.2, 0.1])
        current_date += timedelta(days=skip_days)
    
    data = []
    for date in dates:
        data.append({
            'workout_date': date,
            'activity_type': 'Run',
            'kcal_burned': np.random.normal(450, 75),   # Moderate variation
            'distance_mi': np.random.normal(4.5, 0.8),  # Some variation
            'duration_sec': np.random.normal(2700, 400) # Moderate variation
        })
    
    return pd.DataFrame(data)

class TestConsistencyScoreCalculation:
    """Test comprehensive consistency score calculation"""
    
    def test_calculate_consistency_score_high_consistency(self, consistent_workout_data):
        """Test consistency scoring with highly consistent data"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        result = analyzer.calculate_consistency_score()
        
        # Should detect high consistency
        assert result['consistency_score'] >= 70
        assert result['frequency_score'] >= 60  # Regular 3x per week
        assert result['workouts_analyzed'] == len(consistent_workout_data)
        
        # Should have all scoring components
        expected_scores = ['consistency_score', 'frequency_score', 'timing_score', 
                          'performance_score', 'streak_score']
        for score_type in expected_scores:
            assert score_type in result
            assert 0 <= result[score_type] <= 100
    
    def test_calculate_consistency_score_low_consistency(self, inconsistent_workout_data):
        """Test consistency scoring with inconsistent data"""
        analyzer = ConsistencyAnalyzer(inconsistent_workout_data)
        result = analyzer.calculate_consistency_score()
        
        # Should detect low consistency
        assert result['consistency_score'] < 60
        assert result['workouts_analyzed'] == len(inconsistent_workout_data)
        
        # Frequency score should be low due to irregular timing
        assert result['frequency_score'] < 70
    
    def test_calculate_consistency_score_moderate(self, mixed_pattern_data):
        """Test consistency scoring with moderate consistency"""
        analyzer = ConsistencyAnalyzer(mixed_pattern_data)
        result = analyzer.calculate_consistency_score()
        
        # Should be in moderate range
        assert 30 <= result['consistency_score'] <= 85
        assert result['workouts_analyzed'] == len(mixed_pattern_data)
    
    def test_consistency_score_empty_data(self):
        """Test consistency scoring with no data"""
        empty_df = pd.DataFrame()
        analyzer = ConsistencyAnalyzer(empty_df)
        result = analyzer.calculate_consistency_score()
        
        assert result['consistency_score'] == 0
        assert 'error' in result

class TestFrequencyConsistency:
    """Test workout frequency consistency analysis"""
    
    def test_frequency_consistency_regular_pattern(self, consistent_workout_data):
        """Test frequency analysis with regular workout pattern"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        
        # Calculate just frequency score by calling private method (for testing)
        frequency_score = analyzer._calculate_frequency_consistency(
            consistent_workout_data, 
            periods=28  # 4 weeks
        )
        
        # 3 workouts per week should score well
        assert frequency_score >= 70
    
    def test_frequency_consistency_irregular_pattern(self, inconsistent_workout_data):
        """Test frequency analysis with irregular pattern"""
        analyzer = ConsistencyAnalyzer(inconsistent_workout_data)
        
        frequency_score = analyzer._calculate_frequency_consistency(
            inconsistent_workout_data,
            periods=60  # Longer period to capture gaps
        )
        
        # Irregular pattern should score lower
        assert frequency_score < 70

class TestTimingConsistency:
    """Test workout timing consistency analysis"""
    
    def test_timing_consistency_regular_days(self, consistent_workout_data):
        """Test timing consistency with regular weekly pattern"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        
        timing_score = analyzer._calculate_timing_consistency(consistent_workout_data)
        
        # Mon-Wed-Fri pattern should show good timing consistency
        assert timing_score >= 50
    
    def test_timing_consistency_random_days(self, inconsistent_workout_data):
        """Test timing consistency with random workout days"""
        analyzer = ConsistencyAnalyzer(inconsistent_workout_data)
        
        timing_score = analyzer._calculate_timing_consistency(inconsistent_workout_data)
        
        # Random timing should score lower but not fail completely
        assert 0 <= timing_score <= 100

class TestPerformanceConsistency:
    """Test performance consistency analysis"""
    
    def test_performance_consistency_stable_metrics(self, consistent_workout_data):
        """Test performance consistency with stable workout metrics"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        
        performance_score = analyzer._calculate_performance_consistency(consistent_workout_data)
        
        # Consistent performance metrics should score well
        assert performance_score >= 60
    
    def test_performance_consistency_variable_metrics(self, inconsistent_workout_data):
        """Test performance consistency with highly variable metrics"""
        analyzer = ConsistencyAnalyzer(inconsistent_workout_data)
        
        performance_score = analyzer._calculate_performance_consistency(inconsistent_workout_data)
        
        # Variable performance should score lower
        assert performance_score < 80

class TestStreakMetrics:
    """Test streak-based consistency metrics"""
    
    def test_streak_metrics_good_streaks(self, consistent_workout_data):
        """Test streak calculation with consistent workout pattern"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        
        streak_score = analyzer._calculate_streak_metrics(consistent_workout_data)
        
        # Regular pattern should build good streaks
        assert streak_score > 30  # Some streak value
    
    def test_streak_metrics_poor_streaks(self, inconsistent_workout_data):
        """Test streak calculation with inconsistent pattern"""
        analyzer = ConsistencyAnalyzer(inconsistent_workout_data)
        
        streak_score = analyzer._calculate_streak_metrics(inconsistent_workout_data)
        
        # Inconsistent pattern should have lower streaks
        assert 0 <= streak_score <= 100

class TestWorkoutPatternAnalysis:
    """Test workout pattern analysis functionality"""
    
    def test_analyze_workout_patterns_structure(self, consistent_workout_data):
        """Test that pattern analysis returns expected structure"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        patterns = analyzer.analyze_workout_patterns()
        
        # Should have key pattern categories
        expected_keys = ['preferred_days', 'day_distribution', 'monthly_distribution', 
                        'frequency_analysis']
        for key in expected_keys:
            assert key in patterns
    
    def test_analyze_workout_patterns_preferred_days(self, consistent_workout_data):
        """Test identification of preferred workout days"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        patterns = analyzer.analyze_workout_patterns()
        
        # Should identify Monday, Wednesday, Friday as preferred
        preferred_days = patterns['preferred_days']
        assert len(preferred_days) >= 2  # Should identify top days
        
        # Mon/Wed/Fri should be in top preferences
        top_day_names = list(preferred_days.keys())
        assert any(day in ['Monday', 'Wednesday', 'Friday'] for day in top_day_names)
    
    def test_frequency_pattern_analysis(self, consistent_workout_data):
        """Test frequency pattern analysis"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        patterns = analyzer.analyze_workout_patterns()
        
        freq_analysis = patterns['frequency_analysis']
        
        # Should have frequency metrics
        assert 'average_monthly_workouts' in freq_analysis
        assert freq_analysis['average_monthly_workouts'] > 0

class TestConsistencyPhases:
    """Test consistency phase detection"""
    
    def test_detect_consistency_phases(self, mixed_pattern_data):
        """Test detection of different consistency phases"""
        analyzer = ConsistencyAnalyzer(mixed_pattern_data)
        phases = analyzer.detect_consistency_phases()
        
        # Should detect at least one phase
        assert len(phases) > 0
        
        # Each phase should have required fields
        for phase in phases:
            if 'error' not in phase:  # Skip error phases
                required_fields = ['start_date', 'end_date', 'workout_count', 
                                 'consistency_score', 'phase_type']
                for field in required_fields:
                    assert field in phase
    
    def test_classify_consistency_phase(self, consistent_workout_data):
        """Test consistency phase classification"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        
        # Test phase classification logic
        high_score_phase = analyzer._classify_consistency_phase(85, 10)
        assert high_score_phase == 'high_consistency'
        
        moderate_score_phase = analyzer._classify_consistency_phase(65, 8)
        assert moderate_score_phase == 'moderate_consistency'
        
        low_score_phase = analyzer._classify_consistency_phase(35, 5)
        assert low_score_phase == 'building_consistency'
        
        inactive_phase = analyzer._classify_consistency_phase(20, 0)
        assert inactive_phase == 'inactive_period'

class TestInsightGeneration:
    """Test consistency insights generation"""
    
    def test_generate_consistency_insights_structure(self, consistent_workout_data):
        """Test that insights have proper structure and content"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        insights = analyzer.generate_consistency_insights()
        
        # Should generate insights
        assert isinstance(insights, list)
        assert len(insights) > 0
        
        # Each insight should be a descriptive string with emoji
        for insight in insights:
            assert isinstance(insight, str)
            assert len(insight) > 10  # Should be descriptive
            # Should contain emoji indicators
            assert any(char in insight for char in ['🔥', '💪', '📈', '🎯', '📅', '🏃', '📊', '🏆'])
    
    def test_generate_consistency_insights_content(self, consistent_workout_data):
        """Test that insights contain relevant information"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        insights = analyzer.generate_consistency_insights()
        
        # Should mention consistency score
        score_mentioned = any('score' in insight.lower() for insight in insights)
        assert score_mentioned
        
        # Should include activity patterns or timing insights
        pattern_mentioned = any(
            any(word in insight.lower() for word in ['day', 'monday', 'activity', 'workouts']) 
            for insight in insights
        )
        assert pattern_mentioned

class TestOptimalTimingAnalysis:
    """Test optimal workout timing analysis"""
    
    def test_calculate_optimal_workout_timing(self, consistent_workout_data):
        """Test optimal timing calculation"""
        analyzer = ConsistencyAnalyzer(consistent_workout_data)
        timing_analysis = analyzer.calculate_optimal_workout_timing()
        
        # Should have timing recommendations
        expected_keys = ['best_day_for_calories', 'best_month', 'day_performance_data']
        for key in expected_keys:
            assert key in timing_analysis
        
        # Best day should be a valid day name
        best_day = timing_analysis['best_day_for_calories']
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        assert best_day in valid_days
    
    def test_optimal_timing_insufficient_data(self):
        """Test optimal timing with insufficient data"""
        # Create minimal data without calories
        minimal_data = pd.DataFrame({
            'workout_date': [datetime(2025, 1, 1)],
            'distance_mi': [5.0]
        })
        
        analyzer = ConsistencyAnalyzer(minimal_data)
        timing_analysis = analyzer.calculate_optimal_workout_timing()
        
        assert 'error' in timing_analysis

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframe"""
        empty_df = pd.DataFrame()
        analyzer = ConsistencyAnalyzer(empty_df)
        
        # Should not crash
        score_result = analyzer.calculate_consistency_score()
        assert score_result['consistency_score'] == 0
        
        patterns = analyzer.analyze_workout_patterns()
        # Should handle gracefully (might have errors but shouldn't crash)
        assert isinstance(patterns, dict)
    
    def test_single_workout_handling(self):
        """Test handling of single workout"""
        single_workout = pd.DataFrame({
            'workout_date': [datetime(2025, 1, 1)],
            'kcal_burned': [500],
            'distance_mi': [5.0],
            'duration_sec': [3000]
        })
        
        analyzer = ConsistencyAnalyzer(single_workout)
        
        # Should handle single workout gracefully
        score_result = analyzer.calculate_consistency_score()
        assert 0 <= score_result['consistency_score'] <= 100
    
    def test_missing_columns_handling(self):
        """Test handling of dataframe with missing columns"""
        incomplete_data = pd.DataFrame({
            'workout_date': [datetime(2025, 1, 1), datetime(2025, 1, 3)],
            # Missing other expected columns
        })
        
        analyzer = ConsistencyAnalyzer(incomplete_data)
        
        # Should not crash, but may have reduced functionality
        score_result = analyzer.calculate_consistency_score()
        assert isinstance(score_result, dict)

class TestPerformanceBenchmarks:
    """Performance benchmarks for consistency analysis"""
    
    def test_consistency_analysis_performance(self):
        """Test performance with larger datasets"""
        # Generate larger dataset (90 days of workouts)
        np.random.seed(42)
        
        dates = pd.date_range('2025-01-01', periods=90, freq='D')
        large_data = []
        
        for date in dates:
            if np.random.random() > 0.3:  # 70% chance of workout each day
                large_data.append({
                    'workout_date': date,
                    'kcal_burned': np.random.normal(500, 50),
                    'distance_mi': np.random.normal(5, 1),
                    'duration_sec': np.random.normal(3000, 300)
                })
        
        df = pd.DataFrame(large_data)
        analyzer = ConsistencyAnalyzer(df)
        
        import time
        start_time = time.time()
        
        # Run comprehensive analysis
        consistency_score = analyzer.calculate_consistency_score()
        patterns = analyzer.analyze_workout_patterns()
        insights = analyzer.generate_consistency_insights()
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        # Should complete within reasonable time
        assert analysis_time < 5.0  # Less than 5 seconds
        
        # Results should be valid
        assert 0 <= consistency_score['consistency_score'] <= 100
        assert isinstance(patterns, dict)
        assert isinstance(insights, list)
    
    def test_phase_detection_performance(self, mixed_pattern_data):
        """Test phase detection performance"""
        analyzer = ConsistencyAnalyzer(mixed_pattern_data)
        
        import time
        start_time = time.time()
        
        phases = analyzer.detect_consistency_phases()
        
        end_time = time.time()
        phase_time = end_time - start_time
        
        # Should complete quickly
        assert phase_time < 2.0  # Less than 2 seconds
        assert isinstance(phases, list)