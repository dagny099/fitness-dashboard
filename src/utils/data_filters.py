"""
Generic data filtering utilities for workout analysis.

This module provides reusable filtering functions that can be used across
multiple pages of the fitness dashboard application. The filters support
flexible date-based and metric-based filtering with comprehensive error handling.

Business Context:
- Date filtering is used throughout the app for time-based analysis
- Metric filtering supports performance-based analysis and outlier detection
- Designed for consistency across Intelligence, Choco Effect, Trends, and History views

Author: Fitness Dashboard Team
Last Updated: September 2025
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Union, Tuple
import warnings


def filter_workouts_by_date(
    df: pd.DataFrame,
    days_lookback: Optional[int] = None,
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    reference_date: Optional[datetime] = None
) -> Tuple[pd.DataFrame, dict]:
    """
    Filter workout DataFrame by date range with flexible parameter options.

    This function provides a unified interface for date-based filtering across
    the entire application. It supports multiple ways to specify date ranges
    and handles edge cases gracefully.

    Args:
        df (pd.DataFrame): DataFrame with 'workout_date' column
        days_lookback (int, optional): Number of days back from reference_date.
            Takes precedence over start_date/end_date if provided.
        start_date (str/datetime, optional): Explicit start date for filtering
        end_date (str/datetime, optional): Explicit end date for filtering
        reference_date (datetime, optional): Reference point for days_lookback.
            Defaults to datetime.now() if not provided.

    Returns:
        tuple: (filtered_df, metadata_dict)
            - filtered_df: DataFrame with workouts in specified date range
            - metadata_dict: Contains 'start_date', 'end_date', 'total_filtered',
              'date_range_days', 'filter_method_used'

    Raises:
        ValueError: If df is empty, missing workout_date column, or invalid date parameters

    Examples:
        # Filter last 30 days from today
        filtered_df, meta = filter_workouts_by_date(df, days_lookback=30)

        # Filter specific date range
        filtered_df, meta = filter_workouts_by_date(
            df,
            start_date='2023-01-01',
            end_date='2023-12-31'
        )

        # Filter 90 days back from specific reference point
        ref_date = datetime(2023, 6, 1)
        filtered_df, meta = filter_workouts_by_date(
            df,
            days_lookback=90,
            reference_date=ref_date
        )

    Business Logic Notes:
        - Uses datetime.now() as default reference for "days back" calculations
        - Includes start_date, excludes end_date for consistent behavior
        - Preserves original DataFrame index for traceability
        - Handles timezone-naive dates consistently
    """
    # Input validation
    if df.empty:
        return df.copy(), {
            'start_date': None, 'end_date': None, 'total_filtered': 0,
            'date_range_days': 0, 'filter_method_used': 'empty_input'
        }

    if 'workout_date' not in df.columns:
        raise ValueError("DataFrame must contain 'workout_date' column")

    # Set reference date if not provided
    if reference_date is None:
        reference_date = datetime.now()

    # Ensure workout_date is datetime type
    df_work = df.copy()
    if df_work['workout_date'].dtype == 'object':
        df_work['workout_date'] = pd.to_datetime(df_work['workout_date'])

    # Determine date range based on provided parameters
    if days_lookback is not None:
        # Priority 1: days_lookback approach
        if days_lookback < 0:
            raise ValueError("days_lookback must be positive")

        end_date_calc = reference_date
        start_date_calc = reference_date - timedelta(days=days_lookback)
        filter_method = f"days_lookback_{days_lookback}"

    elif start_date is not None or end_date is not None:
        # Priority 2: explicit date range
        if start_date is not None:
            start_date_calc = pd.to_datetime(start_date) if isinstance(start_date, str) else start_date
        else:
            start_date_calc = df_work['workout_date'].min()

        if end_date is not None:
            end_date_calc = pd.to_datetime(end_date) if isinstance(end_date, str) else end_date
        else:
            end_date_calc = df_work['workout_date'].max()

        filter_method = "explicit_date_range"

    else:
        # No filtering parameters provided - return full dataset
        date_range_days = (df_work['workout_date'].max() - df_work['workout_date'].min()).days
        return df_work, {
            'start_date': df_work['workout_date'].min(),
            'end_date': df_work['workout_date'].max(),
            'total_filtered': len(df_work),
            'date_range_days': date_range_days,
            'filter_method_used': 'no_filter_full_dataset'
        }

    # Validate date range
    if start_date_calc >= end_date_calc:
        warnings.warn(f"start_date ({start_date_calc}) >= end_date ({end_date_calc}). Returning empty DataFrame.")
        return df_work.iloc[0:0], {
            'start_date': start_date_calc, 'end_date': end_date_calc, 'total_filtered': 0,
            'date_range_days': 0, 'filter_method_used': filter_method + '_invalid_range'
        }

    # Apply date filtering (inclusive start, exclusive end for consistency)
    filtered_df = df_work[
        (df_work['workout_date'] >= start_date_calc) &
        (df_work['workout_date'] < end_date_calc)
    ].copy()

    # Calculate metadata
    date_range_days = (end_date_calc - start_date_calc).days

    metadata = {
        'start_date': start_date_calc,
        'end_date': end_date_calc,
        'total_filtered': len(filtered_df),
        'date_range_days': date_range_days,
        'filter_method_used': filter_method
    }

    return filtered_df, metadata


def filter_workouts_by_metrics(
    df: pd.DataFrame,
    min_pace: Optional[float] = None,
    max_pace: Optional[float] = None,
    min_distance: Optional[float] = None,
    max_distance: Optional[float] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
    min_calories: Optional[int] = None,
    max_calories: Optional[int] = None
) -> Tuple[pd.DataFrame, dict]:
    """
    Filter workout DataFrame by performance metrics with outlier detection.

    This function provides metric-based filtering for performance analysis,
    outlier removal, and data quality assurance. All filters are inclusive
    on both bounds (>= min, <= max).

    Args:
        df (pd.DataFrame): DataFrame with workout performance columns
        min_pace (float, optional): Minimum pace in minutes/mile (e.g., 6.0 for 6:00/mile)
        max_pace (float, optional): Maximum pace in minutes/mile (e.g., 15.0 for 15:00/mile)
        min_distance (float, optional): Minimum distance in miles
        max_distance (float, optional): Maximum distance in miles
        min_duration (int, optional): Minimum duration in seconds
        max_duration (int, optional): Maximum duration in seconds
        min_calories (int, optional): Minimum calories burned
        max_calories (int, optional): Maximum calories burned

    Returns:
        tuple: (filtered_df, metadata_dict)
            - filtered_df: DataFrame meeting all metric criteria
            - metadata_dict: Contains filter summary, rows_removed, and applied_filters

    Raises:
        ValueError: If df is empty or required columns are missing

    Examples:
        # Filter for reasonable running paces (6-12 min/mile)
        filtered_df, meta = filter_workouts_by_metrics(
            df,
            min_pace=6.0,
            max_pace=12.0
        )

        # Remove extreme outliers for distance analysis
        filtered_df, meta = filter_workouts_by_metrics(
            df,
            min_distance=0.1,  # Remove GPS errors
            max_distance=50.0,  # Remove ultra-distances
            min_duration=60,    # Remove very short activities
            max_duration=21600  # Remove >6 hour activities
        )

    Business Logic Notes:
        - Designed to handle common data quality issues in fitness tracking
        - Supports both performance analysis and outlier detection use cases
        - Preserves row indices for downstream joining/analysis
        - Handles missing values by excluding them from filtering
    """
    # Input validation
    if df.empty:
        return df.copy(), {
            'total_filtered': 0, 'rows_removed': 0, 'applied_filters': [],
            'filter_summary': 'empty_input'
        }

    df_work = df.copy()
    original_count = len(df_work)
    applied_filters = []

    # Apply pace filtering
    if min_pace is not None:
        if 'avg_pace' not in df_work.columns:
            warnings.warn("avg_pace column not found, skipping pace filtering")
        else:
            df_work = df_work[
                (df_work['avg_pace'].isna()) | (df_work['avg_pace'] >= min_pace)
            ]
            applied_filters.append(f"min_pace >= {min_pace}")

    if max_pace is not None:
        if 'avg_pace' not in df_work.columns:
            warnings.warn("avg_pace column not found, skipping pace filtering")
        else:
            df_work = df_work[
                (df_work['avg_pace'].isna()) | (df_work['avg_pace'] <= max_pace)
            ]
            applied_filters.append(f"max_pace <= {max_pace}")

    # Apply distance filtering
    if min_distance is not None:
        if 'distance_mi' not in df_work.columns:
            warnings.warn("distance_mi column not found, skipping distance filtering")
        else:
            df_work = df_work[
                (df_work['distance_mi'].isna()) | (df_work['distance_mi'] >= min_distance)
            ]
            applied_filters.append(f"min_distance >= {min_distance}")

    if max_distance is not None:
        if 'distance_mi' not in df_work.columns:
            warnings.warn("distance_mi column not found, skipping distance filtering")
        else:
            df_work = df_work[
                (df_work['distance_mi'].isna()) | (df_work['distance_mi'] <= max_distance)
            ]
            applied_filters.append(f"max_distance <= {max_distance}")

    # Apply duration filtering
    if min_duration is not None:
        if 'duration_sec' not in df_work.columns:
            warnings.warn("duration_sec column not found, skipping duration filtering")
        else:
            df_work = df_work[
                (df_work['duration_sec'].isna()) | (df_work['duration_sec'] >= min_duration)
            ]
            applied_filters.append(f"min_duration >= {min_duration}s")

    if max_duration is not None:
        if 'duration_sec' not in df_work.columns:
            warnings.warn("duration_sec column not found, skipping duration filtering")
        else:
            df_work = df_work[
                (df_work['duration_sec'].isna()) | (df_work['duration_sec'] <= max_duration)
            ]
            applied_filters.append(f"max_duration <= {max_duration}s")

    # Apply calorie filtering
    if min_calories is not None:
        if 'kcal_burned' not in df_work.columns:
            warnings.warn("kcal_burned column not found, skipping calorie filtering")
        else:
            df_work = df_work[
                (df_work['kcal_burned'].isna()) | (df_work['kcal_burned'] >= min_calories)
            ]
            applied_filters.append(f"min_calories >= {min_calories}")

    if max_calories is not None:
        if 'kcal_burned' not in df_work.columns:
            warnings.warn("kcal_burned column not found, skipping calorie filtering")
        else:
            df_work = df_work[
                (df_work['kcal_burned'].isna()) | (df_work['kcal_burned'] <= max_calories)
            ]
            applied_filters.append(f"max_calories <= {max_calories}")

    # Calculate metadata
    final_count = len(df_work)
    rows_removed = original_count - final_count

    if not applied_filters:
        filter_summary = "no_filters_applied"
    else:
        filter_summary = f"{len(applied_filters)}_filters_applied"

    metadata = {
        'total_filtered': final_count,
        'rows_removed': rows_removed,
        'applied_filters': applied_filters,
        'filter_summary': filter_summary
    }

    return df_work, metadata


def get_optimal_date_range_suggestion(
    df: pd.DataFrame,
    target_min_workouts: int = 10,
    max_days_back: int = 365
) -> dict:
    """
    Suggest optimal date range to achieve target number of workouts.

    This utility function helps users select appropriate time ranges when
    their initial selection has insufficient data for meaningful analysis.

    Args:
        df (pd.DataFrame): Full workout DataFrame
        target_min_workouts (int): Minimum workouts desired for analysis
        max_days_back (int): Maximum days to look back from current date

    Returns:
        dict: Contains 'suggested_days_back', 'expected_workouts', 'success'

    Business Logic:
        - Helps users understand why they see limited data
        - Provides actionable suggestions for better time ranges
        - Prevents frustration with empty analysis periods
    """
    if df.empty or 'workout_date' not in df.columns:
        return {
            'success': False,
            'suggested_days_back': max_days_back,
            'expected_workouts': 0,
            'message': 'No workout data available'
        }

    # Try different lookback periods to find one that meets target
    for days_back in [7, 14, 30, 60, 90, 180, 365]:
        if days_back > max_days_back:
            break

        filtered_df, _ = filter_workouts_by_date(df, days_lookback=days_back)

        if len(filtered_df) >= target_min_workouts:
            return {
                'success': True,
                'suggested_days_back': days_back,
                'expected_workouts': len(filtered_df),
                'message': f'Suggest looking back {days_back} days for {len(filtered_df)} workouts'
            }

    # If no period works, suggest maximum available
    return {
        'success': False,
        'suggested_days_back': max_days_back,
        'expected_workouts': len(df),
        'message': f'Consider using all available data ({len(df)} total workouts)'
    }