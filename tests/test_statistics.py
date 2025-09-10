"""
tests/test_statistics.py - Tests for statistical analysis utilities

Tests trend analysis, anomaly detection, performance metrics, and statistical insights
that power the AI intelligence system.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.statistics import TrendAnalysis, AnomalyDetection, PerformanceMetrics, StatisticalInsights

@pytest.fixture
def trend_data():
    """Generate sample data with known trends for testing"""
    np.random.seed(42)
    
    # Create ascending trend
    x = np.arange(30)
    ascending_trend = 100 + 2 * x + np.random.normal(0, 5, 30)
    
    # Create descending trend
    descending_trend = 200 - 3 * x + np.random.normal(0, 4, 30)
    
    # Create stable data (no trend)
    stable_data = np.full(30, 150) + np.random.normal(0, 3, 30)
    
    return {
        'ascending': pd.Series(ascending_trend),
        'descending': pd.Series(descending_trend),
        'stable': pd.Series(stable_data),
        'dates': pd.date_range('2025-01-01', periods=30, freq='D')
    }

@pytest.fixture
def anomaly_data():
    """Generate sample data with known anomalies"""
    np.random.seed(42)
    
    # Normal data around mean of 100
    normal_data = np.random.normal(100, 10, 100)
    
    # Insert clear outliers
    normal_data[10] = 200  # High outlier
    normal_data[50] = 20   # Low outlier
    normal_data[80] = 180  # Another high outlier
    
    return pd.Series(normal_data)

class TestTrendAnalysis:
    """Test trend analysis functionality"""
    
    def test_calculate_trend_ascending(self, trend_data):
        """Test detection of ascending trends"""
        result = TrendAnalysis.calculate_trend(trend_data['ascending'])
        
        assert result['trend_direction'] == 'ascending'
        assert result['slope'] > 0
        assert result['confidence'] > 50  # Should be confident about clear trend
        assert result['r_squared'] > 0.3  # Should have reasonable fit
    
    def test_calculate_trend_descending(self, trend_data):
        """Test detection of descending trends"""
        result = TrendAnalysis.calculate_trend(trend_data['descending'])
        
        assert result['trend_direction'] == 'descending'
        assert result['slope'] < 0
        assert result['confidence'] > 50
        assert result['r_squared'] > 0.3
    
    def test_calculate_trend_stable(self, trend_data):
        """Test detection of stable (no trend) data"""
        result = TrendAnalysis.calculate_trend(trend_data['stable'])
        
        # Should detect minimal trend
        assert abs(result['slope']) < 1  # Very small slope
        assert result['r_squared'] < 0.5  # Poor linear fit indicates no trend
    
    def test_calculate_trend_insufficient_data(self):
        """Test trend analysis with insufficient data"""
        insufficient_data = pd.Series([1, 2])
        result = TrendAnalysis.calculate_trend(insufficient_data)
        
        assert result['trend_direction'] == 'insufficient_data'
        assert result['confidence'] == 0
    
    def test_calculate_trend_with_nans(self):
        """Test trend analysis handles NaN values"""
        data_with_nans = pd.Series([1, 2, np.nan, 4, 5, np.nan, 7])
        result = TrendAnalysis.calculate_trend(data_with_nans)
        
        # Should still work by dropping NaN values
        assert result['trend_direction'] in ['ascending', 'descending', 'stable']
        assert not np.isnan(result['slope'])

class TestTrendForecasting:
    """Test forecasting functionality"""
    
    def test_forecast_linear_method(self, trend_data):
        """Test linear forecasting method"""
        forecast = TrendAnalysis.forecast_values(trend_data['ascending'], periods=7, method='linear')
        
        assert len(forecast['forecast']) == 7
        assert len(forecast['confidence_upper']) == 7
        assert len(forecast['confidence_lower']) == 7
        assert forecast['method'] == 'linear'
        
        # Confidence intervals should be reasonable
        for i in range(7):
            assert forecast['confidence_upper'][i] > forecast['forecast'][i]
            assert forecast['confidence_lower'][i] < forecast['forecast'][i]
    
    def test_forecast_moving_average_method(self, trend_data):
        """Test moving average forecasting method"""
        forecast = TrendAnalysis.forecast_values(trend_data['stable'], periods=5, method='moving_average')
        
        assert len(forecast['forecast']) == 5
        assert forecast['method'] == 'moving_average'
        
        # Moving average should predict stable values for stable data
        mean_forecast = np.mean(forecast['forecast'])
        data_mean = trend_data['stable'].mean()
        assert abs(mean_forecast - data_mean) < 20  # Should be close to historical mean
    
    def test_forecast_insufficient_data(self):
        """Test forecasting with insufficient data"""
        insufficient_data = pd.Series([1, 2, 3])
        forecast = TrendAnalysis.forecast_values(insufficient_data, periods=5)
        
        assert 'error' in forecast
        assert forecast['forecast'] == []

class TestAnomalyDetection:
    """Test anomaly detection methods"""
    
    def test_detect_outliers_iqr(self, anomaly_data):
        """Test IQR-based outlier detection"""
        result = AnomalyDetection.detect_outliers(anomaly_data, method='iqr')
        
        assert result['method'] == 'iqr'
        assert result['total_outliers'] >= 2  # Should detect the inserted outliers
        assert result['total_outliers'] <= 10  # But not too many false positives
        assert len(result['outliers']) == result['total_outliers']
        
        # Should detect the extreme values we inserted
        outlier_values = result['outliers']
        assert any(val > 150 for val in outlier_values)  # High outlier
        assert any(val < 50 for val in outlier_values)   # Low outlier
    
    def test_detect_outliers_zscore(self, anomaly_data):
        """Test Z-score based outlier detection"""
        result = AnomalyDetection.detect_outliers(anomaly_data, method='zscore', sensitivity=2.5)
        
        assert result['method'] == 'zscore'
        assert result['total_outliers'] >= 1
        assert result['outlier_percentage'] > 0
    
    def test_detect_outliers_modified_zscore(self, anomaly_data):
        """Test Modified Z-score outlier detection"""
        result = AnomalyDetection.detect_outliers(anomaly_data, method='modified_zscore')
        
        assert result['method'] == 'modified_zscore'
        assert result['total_outliers'] >= 1
    
    def test_detect_outliers_insufficient_data(self):
        """Test outlier detection with insufficient data"""
        small_data = pd.Series([1, 2, 3])
        result = AnomalyDetection.detect_outliers(small_data)
        
        assert result['total_outliers'] == 0
        assert result['outlier_percentage'] == 0

class TestPerformanceAnomalies:
    """Test performance-based anomaly detection"""
    
    def test_detect_performance_anomalies(self):
        """Test performance anomaly detection on workout data"""
        # Create workout dataframe with anomalous performance
        dates = pd.date_range('2025-01-01', periods=30, freq='D')
        
        # Normal pace around 10 min/mile
        normal_pace = np.random.normal(10, 1, 30)
        normal_pace[15] = 25  # Anomalous slow day
        normal_pace[20] = 5   # Anomalous fast day
        
        df = pd.DataFrame({
            'workout_date': dates,
            'avg_pace': normal_pace,
            'distance_mi': np.random.normal(5, 1, 30),
            'duration_sec': np.random.normal(3000, 300, 30)
        })
        
        result = AnomalyDetection.detect_performance_anomalies(df, metric='avg_pace')
        
        assert result['total_anomalies'] >= 1
        assert result['metric_analyzed'] == 'avg_pace'
        assert 'anomalies' in result
    
    def test_detect_performance_anomalies_nonexistent_metric(self):
        """Test performance anomaly detection with non-existent metric"""
        df = pd.DataFrame({'workout_date': [datetime.now()], 'distance_mi': [5.0]})
        
        result = AnomalyDetection.detect_performance_anomalies(df, metric='nonexistent_metric')
        assert 'error' in result

class TestPerformanceMetrics:
    """Test performance metrics calculations"""
    
    def test_calculate_consistency_score_cv(self):
        """Test consistency score using coefficient of variation"""
        # Very consistent data (low CV)
        consistent_data = pd.Series([10, 10.1, 9.9, 10.2, 9.8])
        score = PerformanceMetrics.calculate_consistency_score(consistent_data, method='cv')
        
        assert score > 90  # Should be highly consistent
        
        # Inconsistent data (high CV)
        inconsistent_data = pd.Series([5, 15, 8, 20, 3])
        score = PerformanceMetrics.calculate_consistency_score(inconsistent_data, method='cv')
        
        assert score < 70  # Should be low consistency
    
    def test_calculate_consistency_score_methods(self):
        """Test different consistency calculation methods"""
        test_data = pd.Series([10, 12, 8, 11, 9])
        
        cv_score = PerformanceMetrics.calculate_consistency_score(test_data, method='cv')
        mad_score = PerformanceMetrics.calculate_consistency_score(test_data, method='mad')
        pr_score = PerformanceMetrics.calculate_consistency_score(test_data, method='percentile_range')
        
        # All methods should return scores between 0-100
        assert 0 <= cv_score <= 100
        assert 0 <= mad_score <= 100
        assert 0 <= pr_score <= 100
    
    def test_calculate_improvement_rate(self, trend_data):
        """Test improvement rate calculation"""
        # Should detect improvement in ascending trend
        improvement = PerformanceMetrics.calculate_improvement_rate(trend_data['ascending'])
        
        assert improvement['improvement_rate'] > 0  # Positive improvement
        assert improvement['is_improving'] == True
        assert 0 <= improvement['improvement_confidence'] <= 100
        
        # Should detect decline in descending trend
        decline = PerformanceMetrics.calculate_improvement_rate(trend_data['descending'])
        
        assert decline['improvement_rate'] < 0  # Negative improvement (decline)
        assert decline['is_improving'] == False
    
    def test_detect_plateaus(self):
        """Test plateau detection in performance data"""
        # Create data with a clear plateau
        plateau_data = []
        
        # Rising phase
        plateau_data.extend(range(10, 20))
        # Plateau phase (stable for 10 points)
        plateau_data.extend([20] * 10)
        # Rising again
        plateau_data.extend(range(21, 25))
        
        plateau_series = pd.Series(plateau_data)
        plateaus = PerformanceMetrics.detect_plateaus(plateau_series, min_length=8, threshold=0.02)
        
        assert len(plateaus) >= 1  # Should detect at least one plateau
        
        # Check plateau properties
        plateau = plateaus[0] if plateaus else None
        if plateau:
            assert plateau['duration_days'] >= 8
            assert plateau['stability'] > 80  # Should be stable

class TestStatisticalInsights:
    """Test statistical insights generation"""
    
    def test_generate_trend_insight(self, trend_data):
        """Test trend insight generation"""
        trend_result = TrendAnalysis.calculate_trend(trend_data['ascending'])
        insight = StatisticalInsights.generate_trend_insight(trend_result, 'calories')
        
        assert isinstance(insight, str)
        assert 'calories' in insight.lower()
        assert len(insight) > 10  # Should be descriptive
        
        # Should mention trend direction
        if trend_result['confidence'] > 30:
            assert any(word in insight.lower() for word in ['improving', 'ascending', 'increasing'])
    
    def test_generate_anomaly_insight(self, anomaly_data):
        """Test anomaly insight generation"""
        anomaly_result = AnomalyDetection.detect_outliers(anomaly_data)
        insights = StatisticalInsights.generate_anomaly_insight(anomaly_result, 'distance')
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        
        for insight in insights:
            assert isinstance(insight, str)
            assert 'distance' in insight.lower()
    
    def test_generate_performance_insight(self, trend_data):
        """Test performance insight generation"""
        improvement_result = PerformanceMetrics.calculate_improvement_rate(trend_data['ascending'])
        insight = StatisticalInsights.generate_performance_insight(improvement_result, 'pace')
        
        assert isinstance(insight, str)
        assert 'pace' in insight.lower()
        assert len(insight) > 10

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_data_handling(self):
        """Test all methods handle empty data gracefully"""
        empty_series = pd.Series([])
        
        # Trend analysis
        trend_result = TrendAnalysis.calculate_trend(empty_series)
        assert trend_result['trend_direction'] == 'insufficient_data'
        
        # Anomaly detection
        anomaly_result = AnomalyDetection.detect_outliers(empty_series)
        assert anomaly_result['total_outliers'] == 0
        
        # Performance metrics
        consistency_score = PerformanceMetrics.calculate_consistency_score(empty_series)
        assert consistency_score == 0.0
        
        improvement_rate = PerformanceMetrics.calculate_improvement_rate(empty_series)
        assert improvement_rate['improvement_rate'] == 0
    
    def test_single_value_data(self):
        """Test handling of single data point"""
        single_value = pd.Series([42])
        
        trend_result = TrendAnalysis.calculate_trend(single_value)
        assert trend_result['trend_direction'] == 'insufficient_data'
        
        consistency_score = PerformanceMetrics.calculate_consistency_score(single_value)
        assert consistency_score == 0.0
    
    def test_all_identical_values(self):
        """Test handling of data with no variation"""
        identical_data = pd.Series([10, 10, 10, 10, 10])
        
        # Should handle zero variance gracefully
        consistency_score = PerformanceMetrics.calculate_consistency_score(identical_data)
        assert consistency_score == 100.0  # Perfect consistency
        
        anomaly_result = AnomalyDetection.detect_outliers(identical_data)
        assert anomaly_result['total_outliers'] == 0  # No outliers in identical data

class TestPerformanceBenchmarks:
    """Performance benchmarks for statistical operations"""
    
    def test_trend_analysis_performance(self):
        """Test trend analysis performance with large datasets"""
        large_dataset = pd.Series(np.random.normal(100, 10, 10000))
        
        import time
        start_time = time.time()
        
        result = TrendAnalysis.calculate_trend(large_dataset)
        
        end_time = time.time()
        analysis_time = end_time - start_time
        
        # Should complete quickly even with large data
        assert analysis_time < 1.0  # Less than 1 second
        assert result['trend_direction'] in ['ascending', 'descending', 'stable']
    
    def test_anomaly_detection_performance(self):
        """Test anomaly detection performance"""
        large_dataset = pd.Series(np.random.normal(100, 10, 5000))
        
        import time
        start_time = time.time()
        
        result = AnomalyDetection.detect_outliers(large_dataset, method='iqr')
        
        end_time = time.time()
        detection_time = end_time - start_time
        
        # Should complete quickly
        assert detection_time < 2.0  # Less than 2 seconds
        assert 'total_outliers' in result
    
    def test_forecasting_performance(self, trend_data):
        """Test forecasting performance"""
        import time
        start_time = time.time()
        
        forecast = TrendAnalysis.forecast_values(trend_data['ascending'], periods=30)
        
        end_time = time.time()
        forecast_time = end_time - start_time
        
        # Should complete quickly
        assert forecast_time < 1.0  # Less than 1 second
        assert len(forecast['forecast']) == 30