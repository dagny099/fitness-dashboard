"""
Comprehensive unit tests for data filtering utilities.

Tests cover date boundary conditions, edge cases, and business logic
to ensure reliable filtering behavior across the fitness dashboard.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from src.utils.data_filters import (
    filter_workouts_by_date,
    filter_workouts_by_metrics,
    get_optimal_date_range_suggestion
)


class TestDateFiltering:
    """Test suite for workout date filtering functionality."""

    def setup_method(self):
        """Set up test data for each test method."""
        # Create sample workout data with different dates
        base_date = datetime(2023, 6, 1)
        dates = [base_date + timedelta(days=i) for i in range(100)]

        self.sample_df = pd.DataFrame({
            'workout_date': dates,
            'distance_mi': np.random.uniform(1, 10, 100),
            'avg_pace': np.random.uniform(7, 15, 100),
            'duration_sec': np.random.uniform(1800, 3600, 100)
        })

    def test_days_lookback_filtering(self):
        """Test basic days_lookback filtering functionality."""
        reference_date = datetime(2023, 6, 50)  # Middle of our test range

        filtered_df, metadata = filter_workouts_by_date(
            self.sample_df,
            days_lookback=10,
            reference_date=reference_date
        )

        # Should get workouts from 10 days back
        expected_start = reference_date - timedelta(days=10)
        assert metadata['start_date'] == expected_start
        assert metadata['end_date'] == reference_date
        assert metadata['filter_method_used'] == 'days_lookback_10'
        assert len(filtered_df) == 10  # Exactly 10 days of data

    def test_explicit_date_range_filtering(self):
        """Test filtering with explicit start and end dates."""
        start_date = datetime(2023, 6, 20)
        end_date = datetime(2023, 6, 30)

        filtered_df, metadata = filter_workouts_by_date(
            self.sample_df,
            start_date=start_date,
            end_date=end_date
        )

        assert metadata['start_date'] == start_date
        assert metadata['end_date'] == end_date
        assert metadata['filter_method_used'] == 'explicit_date_range'
        assert len(filtered_df) == 10  # 10 days inclusive start, exclusive end

    def test_date_boundary_conditions(self):
        """Test edge cases around date boundaries."""
        # Test same start and end date
        same_date = datetime(2023, 6, 15)

        filtered_df, metadata = filter_workouts_by_date(
            self.sample_df,
            start_date=same_date,
            end_date=same_date
        )

        # Should return empty DataFrame with warning metadata
        assert len(filtered_df) == 0
        assert 'invalid_range' in metadata['filter_method_used']

    def test_choco_effect_date_boundary(self):
        """Test filtering around the Choco Effect date boundary."""
        # Create data spanning the Choco Effect date
        choco_date = datetime(2018, 6, 1)
        pre_choco_dates = [choco_date - timedelta(days=i) for i in range(10, 0, -1)]
        post_choco_dates = [choco_date + timedelta(days=i) for i in range(10)]

        boundary_df = pd.DataFrame({
            'workout_date': pre_choco_dates + post_choco_dates,
            'distance_mi': np.random.uniform(1, 5, 20),
            'avg_pace': np.random.uniform(8, 25, 20),
            'duration_sec': np.random.uniform(1800, 5400, 20)
        })

        # Filter for just the transition period
        filtered_df, metadata = filter_workouts_by_date(
            boundary_df,
            start_date=choco_date - timedelta(days=5),
            end_date=choco_date + timedelta(days=5)
        )

        # Should get workouts from both eras
        pre_choco_count = len(filtered_df[filtered_df['workout_date'] < choco_date])
        post_choco_count = len(filtered_df[filtered_df['workout_date'] >= choco_date])

        assert pre_choco_count == 5
        assert post_choco_count == 5
        assert metadata['date_range_days'] == 10

    def test_empty_dataframe_handling(self):
        """Test behavior with empty input DataFrame."""
        empty_df = pd.DataFrame()

        filtered_df, metadata = filter_workouts_by_date(
            empty_df,
            days_lookback=30
        )

        assert filtered_df.empty
        assert metadata['total_filtered'] == 0
        assert metadata['filter_method_used'] == 'empty_input'

    def test_missing_workout_date_column(self):
        """Test error handling for missing workout_date column."""
        invalid_df = pd.DataFrame({
            'distance_mi': [1, 2, 3],
            'pace': [8, 9, 10]
        })

        with pytest.raises(ValueError, match="must contain 'workout_date' column"):
            filter_workouts_by_date(invalid_df, days_lookback=30)

    def test_string_date_conversion(self):
        """Test automatic conversion of string dates to datetime."""
        string_date_df = pd.DataFrame({
            'workout_date': ['2023-06-01', '2023-06-02', '2023-06-03'],
            'distance_mi': [1, 2, 3]
        })

        filtered_df, metadata = filter_workouts_by_date(
            string_date_df,
            start_date='2023-06-01',
            end_date='2023-06-03'
        )

        assert len(filtered_df) == 2  # Exclusive end date
        assert pd.api.types.is_datetime64_any_dtype(filtered_df['workout_date'])

    def test_future_date_handling(self):
        """Test handling of future dates in filtering."""
        future_date = datetime.now() + timedelta(days=365)

        # Should return empty result when filtering for future dates
        filtered_df, metadata = filter_workouts_by_date(
            self.sample_df,
            start_date=future_date,
            end_date=future_date + timedelta(days=10)
        )

        assert len(filtered_df) == 0

    def test_current_date_as_reference(self):
        """Test that datetime.now() is used as default reference."""
        # Create data with recent dates
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_dates = [today - timedelta(days=i) for i in range(30)]

        recent_df = pd.DataFrame({
            'workout_date': recent_dates,
            'distance_mi': np.random.uniform(1, 5, 30)
        })

        filtered_df, metadata = filter_workouts_by_date(
            recent_df,
            days_lookback=7
        )

        # Should get last 7 days of workouts
        assert len(filtered_df) == 7
        assert metadata['end_date'].date() >= today.date()


class TestMetricFiltering:
    """Test suite for workout metric filtering functionality."""

    def setup_method(self):
        """Set up test data for metric filtering tests."""
        self.metric_df = pd.DataFrame({
            'avg_pace': [6.0, 8.5, 12.0, 15.5, 25.0, 45.0],  # Mix of fast/slow paces
            'distance_mi': [1.0, 3.2, 5.5, 2.1, 1.8, 0.1],   # Various distances
            'duration_sec': [600, 1800, 3600, 2400, 5400, 60], # Different durations
            'kcal_burned': [100, 300, 550, 280, 450, 50]       # Calorie range
        })

    def test_pace_filtering(self):
        """Test pace-based filtering for running workouts."""
        # Filter for reasonable running paces (6-12 min/mile)
        filtered_df, metadata = filter_workouts_by_metrics(
            self.metric_df,
            min_pace=6.0,
            max_pace=12.0
        )

        assert len(filtered_df) == 3  # Should get first 3 rows
        assert all(filtered_df['avg_pace'] >= 6.0)
        assert all(filtered_df['avg_pace'] <= 12.0)
        assert 'min_pace >= 6.0' in metadata['applied_filters']
        assert 'max_pace <= 12.0' in metadata['applied_filters']

    def test_outlier_removal(self):
        """Test removal of extreme outlier values."""
        filtered_df, metadata = filter_workouts_by_metrics(
            self.metric_df,
            max_pace=30.0,  # Remove extremely slow paces
            min_distance=0.5,  # Remove very short distances
            min_duration=300   # Remove very short workouts
        )

        # Should remove the 45.0 pace, 0.1 distance, and 60 second workout
        assert len(filtered_df) < len(self.metric_df)
        assert metadata['rows_removed'] > 0
        assert all(filtered_df['avg_pace'] <= 30.0)
        assert all(filtered_df['distance_mi'] >= 0.5)
        assert all(filtered_df['duration_sec'] >= 300)

    def test_missing_column_handling(self):
        """Test graceful handling of missing columns."""
        incomplete_df = pd.DataFrame({
            'distance_mi': [1, 2, 3]
            # Missing avg_pace column
        })

        # Should complete without error, just skip pace filtering
        filtered_df, metadata = filter_workouts_by_metrics(
            incomplete_df,
            min_pace=8.0,
            max_pace=12.0
        )

        assert len(filtered_df) == 3  # All rows should remain
        assert metadata['applied_filters'] == []  # No filters applied

    def test_multiple_metric_filtering(self):
        """Test filtering on multiple metrics simultaneously."""
        filtered_df, metadata = filter_workouts_by_metrics(
            self.metric_df,
            min_pace=7.0,
            max_pace=20.0,
            min_distance=1.5,
            max_distance=10.0,
            min_calories=200
        )

        # Should apply all filters
        assert len(metadata['applied_filters']) == 5
        assert all(filtered_df['avg_pace'] >= 7.0)
        assert all(filtered_df['avg_pace'] <= 20.0)
        assert all(filtered_df['distance_mi'] >= 1.5)
        assert all(filtered_df['distance_mi'] <= 10.0)
        assert all(filtered_df['kcal_burned'] >= 200)

    def test_nan_value_handling(self):
        """Test proper handling of NaN values in metrics."""
        nan_df = pd.DataFrame({
            'avg_pace': [8.0, np.nan, 10.0, 12.0],
            'distance_mi': [2.0, 3.0, np.nan, 4.0]
        })

        filtered_df, metadata = filter_workouts_by_metrics(
            nan_df,
            min_pace=9.0,
            min_distance=2.5
        )

        # NaN values should be preserved (not filtered out)
        assert len(filtered_df[filtered_df['avg_pace'].isna()]) == 1
        assert len(filtered_df[filtered_df['distance_mi'].isna()]) == 1


class TestOptimalDateRangeSuggestion:
    """Test suite for optimal date range suggestion functionality."""

    def setup_method(self):
        """Set up test data for suggestion tests."""
        # Create sparse workout data
        dates = []
        current_date = datetime.now()

        # Add workouts at irregular intervals
        for i in [1, 3, 7, 14, 30, 45, 60, 90, 120, 180, 300, 350]:
            dates.append(current_date - timedelta(days=i))

        self.sparse_df = pd.DataFrame({
            'workout_date': dates,
            'distance_mi': [1] * len(dates)
        })

    def test_sufficient_data_suggestion(self):
        """Test suggestion when sufficient data exists in short timeframe."""
        suggestion = get_optimal_date_range_suggestion(
            self.sparse_df,
            target_min_workouts=5,
            max_days_back=365
        )

        assert suggestion['success'] is True
        assert suggestion['expected_workouts'] >= 5
        assert suggestion['suggested_days_back'] <= 365

    def test_insufficient_data_handling(self):
        """Test suggestion when insufficient data exists."""
        # Create DataFrame with very few workouts
        minimal_df = pd.DataFrame({
            'workout_date': [datetime.now() - timedelta(days=300)],
            'distance_mi': [1]
        })

        suggestion = get_optimal_date_range_suggestion(
            minimal_df,
            target_min_workouts=10,
            max_days_back=200  # Less than where the workout is
        )

        assert suggestion['success'] is False
        assert suggestion['suggested_days_back'] == 200
        assert 'Consider using all available data' in suggestion['message']

    def test_empty_dataframe_suggestion(self):
        """Test suggestion behavior with empty DataFrame."""
        empty_df = pd.DataFrame()

        suggestion = get_optimal_date_range_suggestion(
            empty_df,
            target_min_workouts=5
        )

        assert suggestion['success'] is False
        assert suggestion['expected_workouts'] == 0
        assert 'No workout data available' in suggestion['message']

    def test_progressive_timeframe_search(self):
        """Test that suggestion tries progressively longer timeframes."""
        # This should find the optimal timeframe without going to maximum
        suggestion = get_optimal_date_range_suggestion(
            self.sparse_df,
            target_min_workouts=8,
            max_days_back=365
        )

        assert suggestion['success'] is True
        assert suggestion['suggested_days_back'] < 365  # Should find optimal before max


class TestBusinessLogicIntegration:
    """Test business logic integration and real-world scenarios."""

    def test_choco_effect_era_classification_data(self):
        """Test filtering behavior around Choco Effect transition for classification."""
        choco_date = datetime(2018, 6, 1)

        # Create realistic data spanning the transition
        pre_dates = [choco_date - timedelta(days=i) for i in range(365, 0, -1)]
        post_dates = [choco_date + timedelta(days=i) for i in range(365)]

        all_dates = pre_dates + post_dates

        # Simulate different activity patterns pre/post Choco
        pre_paces = np.random.normal(9.0, 1.5, 365)  # Running-focused
        post_paces = np.random.normal(22.0, 3.0, 365)  # Walking-focused

        transition_df = pd.DataFrame({
            'workout_date': all_dates,
            'avg_pace': np.concatenate([pre_paces, post_paces]),
            'distance_mi': np.random.uniform(1, 5, 730)
        })

        # Test filtering around the transition date
        filtered_df, metadata = filter_workouts_by_date(
            transition_df,
            start_date=choco_date - timedelta(days=30),
            end_date=choco_date + timedelta(days=30)
        )

        assert len(filtered_df) == 60  # 30 days before + 30 days after

        # Verify we have data from both eras
        pre_era_count = len(filtered_df[filtered_df['workout_date'] < choco_date])
        post_era_count = len(filtered_df[filtered_df['workout_date'] >= choco_date])

        assert pre_era_count == 30
        assert post_era_count == 30

    def test_realistic_workout_data_filtering(self):
        """Test filtering with realistic workout data patterns."""
        # Simulate realistic workout patterns
        current_date = datetime.now()
        workout_dates = []

        # Simulate 3 workouts per week for last 12 weeks
        for week in range(12):
            week_start = current_date - timedelta(weeks=week)
            # Add workouts on Monday, Wednesday, Friday
            for day_offset in [0, 2, 4]:
                workout_dates.append(week_start - timedelta(days=day_offset))

        realistic_df = pd.DataFrame({
            'workout_date': workout_dates,
            'distance_mi': np.random.uniform(2, 6, len(workout_dates)),
            'avg_pace': np.random.uniform(8, 12, len(workout_dates)),
            'duration_sec': np.random.uniform(1800, 4500, len(workout_dates)),
            'kcal_burned': np.random.uniform(250, 600, len(workout_dates))
        })

        # Test 30-day filtering (should get ~12-13 workouts)
        filtered_df, metadata = filter_workouts_by_date(
            realistic_df,
            days_lookback=30
        )

        expected_workouts = 12  # ~3 per week * 4 weeks
        assert len(filtered_df) >= expected_workouts - 2  # Allow some variance
        assert len(filtered_df) <= expected_workouts + 2

    def test_data_quality_filtering_scenario(self):
        """Test combined date and metric filtering for data quality."""
        # Create data with quality issues
        base_date = datetime.now() - timedelta(days=60)
        problematic_df = pd.DataFrame({
            'workout_date': [base_date + timedelta(days=i) for i in range(20)],
            'avg_pace': [8, 9, 150, 10, 11, 0.5, 12, 13, -1, 14,  # Outliers mixed in
                        15, 16, 200, 17, 18, 19, 20, 21, 22, 23],
            'distance_mi': [3, 4, 0.01, 5, 6, 100, 2, 3, 4, 5,  # GPS errors
                           6, 7, 8, 9, 2, 3, 4, 5, 6, 7],
            'duration_sec': [1800, 2400, 50, 3600, 3000, 86400, 2700, 1800,  # Time errors
                            2400, 3600, 3000, 2700, 1800, 2400, 3600, 3000,
                            2700, 1800, 2400, 3600]
        })

        # Apply realistic data quality filters
        clean_df, metric_meta = filter_workouts_by_metrics(
            problematic_df,
            min_pace=5.0,      # Remove impossible fast paces
            max_pace=30.0,     # Remove impossible slow paces
            min_distance=0.1,   # Remove GPS errors
            max_distance=50.0,  # Remove GPS errors
            min_duration=300,   # Remove very short activities
            max_duration=21600  # Remove impossibly long activities (6 hours)
        )

        # Then filter by date
        final_df, date_meta = filter_workouts_by_date(
            clean_df,
            days_lookback=30
        )

        # Should have removed problematic data
        assert len(final_df) < len(problematic_df)
        assert metric_meta['rows_removed'] > 0
        assert all(final_df['avg_pace'] >= 5.0)
        assert all(final_df['avg_pace'] <= 30.0)
        assert all(final_df['distance_mi'] >= 0.1)
        assert all(final_df['distance_mi'] <= 50.0)


if __name__ == '__main__':
    pytest.main([__file__])