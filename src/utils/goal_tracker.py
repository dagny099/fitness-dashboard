"""
Goal tracking utilities for personalized fitness goals.

This module provides comprehensive goal tracking and adherence metrics for:
- Walk/distance goals (daily targets, weekly/monthly adherence)
- Run frequency goals (days between runs, consistency)
- Pace achievement goals (runs meeting target pace)

Designed to integrate with the Personalized Goals section of the AI Intelligence dashboard.

Author: Fitness Dashboard Team
Created: October 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta


class GoalTracker:
    """Track goal adherence and performance metrics over time."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize goal tracker with workout data.

        Args:
            df: DataFrame with workout data including:
                - workout_date: Date of workout
                - predicted_activity_type: ML classification (real_run, pup_walk, etc.)
                - distance_mi: Distance in miles
                - avg_pace: Average pace in min/mile

        Raises:
            ValueError: If df is empty or missing required columns
        """
        if df.empty:
            raise ValueError("Cannot initialize GoalTracker with empty DataFrame")

        required_columns = ['workout_date', 'predicted_activity_type']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"DataFrame missing required columns: {missing_cols}")

        self.df = df.copy()
        # Ensure workout_date is datetime
        if self.df['workout_date'].dtype == 'object':
            self.df['workout_date'] = pd.to_datetime(self.df['workout_date'])

        # Sort by date for gap calculations
        self.df = self.df.sort_values('workout_date')

    def get_date_ranges(self, reference_date: Optional[datetime] = None) -> Dict[str, datetime]:
        """
        Calculate standard date ranges for goal tracking.

        Args:
            reference_date: Date to use as "today" (defaults to datetime.now())

        Returns:
            Dictionary containing start/end dates for:
            - this_week_start, this_week_end
            - last_week_start, last_week_end
            - this_month_start, this_month_end
            - last_month_start, last_month_end
            - same_month_last_year_start, same_month_last_year_end

        Business Logic:
            - Week starts on Monday (ISO standard)
            - Month boundaries are calendar months
            - "Same month last year" = exact same calendar month 1 year prior
        """
        if reference_date is None:
            reference_date = datetime.now()

        # Normalize to date (no time component)
        ref_date = reference_date.date() if isinstance(reference_date, datetime) else reference_date
        ref_datetime = datetime.combine(ref_date, datetime.min.time())

        # This week (Monday to Sunday)
        days_since_monday = ref_datetime.weekday()  # Monday = 0
        this_week_start = ref_datetime - timedelta(days=days_since_monday)
        this_week_end = this_week_start + timedelta(days=7)

        # Last week
        last_week_end = this_week_start
        last_week_start = last_week_end - timedelta(days=7)

        # This month
        this_month_start = ref_datetime.replace(day=1)
        # Next month's first day
        if ref_datetime.month == 12:
            this_month_end = ref_datetime.replace(year=ref_datetime.year + 1, month=1, day=1)
        else:
            this_month_end = ref_datetime.replace(month=ref_datetime.month + 1, day=1)

        # Last month
        last_month_end = this_month_start
        if this_month_start.month == 1:
            last_month_start = this_month_start.replace(year=this_month_start.year - 1, month=12, day=1)
        else:
            last_month_start = this_month_start.replace(month=this_month_start.month - 1, day=1)

        # Same month last year
        try:
            same_month_last_year_start = this_month_start.replace(year=this_month_start.year - 1)
            same_month_last_year_end = this_month_end.replace(year=this_month_end.year - 1)
        except ValueError:
            # Handle Feb 29 edge case
            same_month_last_year_start = this_month_start.replace(year=this_month_start.year - 1, day=28)
            same_month_last_year_end = this_month_end.replace(year=this_month_end.year - 1)

        return {
            'this_week_start': this_week_start,
            'this_week_end': this_week_end,
            'last_week_start': last_week_start,
            'last_week_end': last_week_end,
            'this_month_start': this_month_start,
            'this_month_end': this_month_end,
            'last_month_start': last_month_start,
            'last_month_end': last_month_end,
            'same_month_last_year_start': same_month_last_year_start,
            'same_month_last_year_end': same_month_last_year_end,
            'reference_date': ref_datetime
        }

    def get_period_relative_date_ranges(
        self,
        days_lookback: int,
        reference_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate period-relative date ranges for apples-to-apples comparisons.

        This method creates equal-length, non-overlapping time periods for fair
        performance comparisons. Unlike calendar-based periods (this month vs last month),
        these rolling periods ensure consistent comparison windows.

        Args:
            days_lookback: Number of days in the analysis period (e.g., 7, 30, 90, 365)
            reference_date: Reference point for "today" (defaults to datetime.now())

        Returns:
            Dictionary containing:
            - current_period_start: Start of selected period (days_lookback days ago)
            - current_period_end: End of selected period (reference_date)
            - previous_period_start: Start of prior period (2*days_lookback days ago)
            - previous_period_end: End of prior period (days_lookback days ago)
            - year_ago_period_start: Same period, 1 year earlier
            - year_ago_period_end: Same period end, 1 year earlier
            - period_length_days: days_lookback (for display/validation)

        Example:
            For days_lookback=30 on Oct 1, 2025:
            - Current period: Sept 1 - Sept 30 (30 days)
            - Previous period: Aug 1 - Aug 31 (30 days)
            - Year ago period: Sept 1 - Sept 30, 2024 (30 days)

        Business Logic:
            - All periods are exactly the same length
            - Current and previous periods do not overlap (clean comparisons)
            - Year-ago period is the exact same calendar window from 1 year prior
            - Works correctly on any day (day 1 of month, leap years, etc.)
        """
        if reference_date is None:
            reference_date = datetime.now()

        # Normalize to datetime
        if not isinstance(reference_date, datetime):
            reference_date = datetime.combine(reference_date, datetime.min.time())

        # Current period: last N days ending at reference date
        current_period_end = reference_date
        current_period_start = reference_date - timedelta(days=days_lookback)

        # Previous period: prior N days (non-overlapping)
        previous_period_end = current_period_start
        previous_period_start = previous_period_end - timedelta(days=days_lookback)

        # Year-ago period: same N days, one year earlier
        year_ago_period_end = current_period_end - timedelta(days=365)
        year_ago_period_start = current_period_start - timedelta(days=365)

        return {
            'current_period_start': current_period_start,
            'current_period_end': current_period_end,
            'previous_period_start': previous_period_start,
            'previous_period_end': previous_period_end,
            'year_ago_period_start': year_ago_period_start,
            'year_ago_period_end': year_ago_period_end,
            'period_length_days': days_lookback
        }

    def calculate_walk_goal_adherence(
        self,
        target_distance: float,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate walk goal adherence for a time period.

        Measures how many days the user met their daily walk distance target.

        Args:
            target_distance: Target daily distance in miles
            start_date: Start of period (inclusive)
            end_date: End of period (exclusive)

        Returns:
            Dictionary containing:
            - days_met_goal: Number of days hitting or exceeding target
            - total_days_with_walks: Number of days with at least one walk
            - pct_days_met_goal: Percentage of walk days meeting goal (0-100)
            - avg_distance: Average daily distance on days with walks
            - total_walks: Total number of walk workouts
            - period_days: Total days in period

        Business Logic:
            - Only counts days with pup_walk activities
            - If multiple walks on same day, sums the distances
            - Returns 0% if no walks in period (not N/A) for consistent comparison
        """
        # Filter to date range
        period_df = self.df[
            (self.df['workout_date'] >= start_date) &
            (self.df['workout_date'] < end_date)
        ].copy()

        # Filter to walks only
        walks_df = period_df[period_df['predicted_activity_type'] == 'pup_walk'].copy()

        if walks_df.empty:
            period_days = (end_date - start_date).days
            return {
                'days_met_goal': 0,
                'total_days_with_walks': 0,
                'pct_days_met_goal': 0.0,
                'avg_distance': 0.0,
                'total_walks': 0,
                'period_days': period_days
            }

        # Check if distance_mi column exists
        if 'distance_mi' not in walks_df.columns:
            return {
                'days_met_goal': 0,
                'total_days_with_walks': len(walks_df),
                'pct_days_met_goal': 0.0,
                'avg_distance': 0.0,
                'total_walks': len(walks_df),
                'period_days': (end_date - start_date).days,
                'error': 'distance_mi column not available'
            }

        # Sum distances by day (handles multiple walks per day)
        walks_df['date_only'] = walks_df['workout_date'].dt.date
        daily_distances = walks_df.groupby('date_only')['distance_mi'].sum()

        # Calculate metrics
        days_met_goal = (daily_distances >= target_distance).sum()
        total_days_with_walks = len(daily_distances)
        pct_days_met_goal = (days_met_goal / total_days_with_walks * 100) if total_days_with_walks > 0 else 0.0
        avg_distance = daily_distances.mean()
        total_walks = len(walks_df)
        period_days = (end_date - start_date).days

        return {
            'days_met_goal': int(days_met_goal),
            'total_days_with_walks': int(total_days_with_walks),
            'pct_days_met_goal': float(pct_days_met_goal),
            'avg_distance': float(avg_distance),
            'total_walks': int(total_walks),
            'period_days': period_days
        }

    def calculate_days_since_last_run(
        self,
        reference_date: Optional[datetime] = None
    ) -> int:
        """
        Calculate days since most recent real_run.

        Args:
            reference_date: Date to measure from (defaults to datetime.now())

        Returns:
            Number of days since last run (0 if run today, -1 if no runs found)

        Business Logic:
            - Only counts predicted_activity_type == 'real_run'
            - Returns -1 if no runs in entire dataset (clear error signal)
            - Returns 0 if most recent run was today
        """
        if reference_date is None:
            reference_date = datetime.now()

        # Normalize to date for comparison
        ref_date = reference_date.date() if isinstance(reference_date, datetime) else reference_date

        # Filter to runs only
        runs_df = self.df[self.df['predicted_activity_type'] == 'real_run'].copy()

        if runs_df.empty:
            return -1  # No runs found

        # Get most recent run date
        most_recent_run = runs_df['workout_date'].max()
        most_recent_run_date = most_recent_run.date() if isinstance(most_recent_run, datetime) else most_recent_run

        # Calculate days difference
        days_since = (ref_date - most_recent_run_date).days

        return max(0, days_since)  # Don't return negative (future runs)

    def calculate_avg_days_between_runs(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Calculate average number of days between consecutive runs in a period.

        Args:
            start_date: Start of period (inclusive)
            end_date: End of period (exclusive)

        Returns:
            Average days between runs (returns -1 if < 2 runs in period)

        Business Logic:
            - Only counts predicted_activity_type == 'real_run'
            - Needs at least 2 runs to calculate gaps
            - Returns -1 if insufficient data (not 0, to signal "N/A")

        Example:
            Runs on: Jan 1, Jan 5, Jan 12
            Gaps: 4 days, 7 days
            Average: 5.5 days
        """
        # Filter to date range
        period_df = self.df[
            (self.df['workout_date'] >= start_date) &
            (self.df['workout_date'] < end_date)
        ].copy()

        # Filter to runs only
        runs_df = period_df[period_df['predicted_activity_type'] == 'real_run'].copy()

        if len(runs_df) < 2:
            return -1.0  # Need at least 2 runs to calculate gaps

        # Sort by date (should already be sorted from __init__)
        runs_df = runs_df.sort_values('workout_date')

        # Calculate gaps between consecutive runs
        gaps = runs_df['workout_date'].diff().dt.days

        # Drop the first NaN value (no gap before first run)
        gaps = gaps.dropna()

        if len(gaps) == 0:
            return -1.0

        avg_gap = gaps.mean()

        return float(avg_gap)

    def count_runs_below_pace(
        self,
        target_pace: float,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Count how many runs achieved better than target pace.

        Note: "Below" pace means faster (e.g., 9 min/mi is below/better than 10 min/mi)

        Args:
            target_pace: Target pace in min/mile
            start_date: Start of period (inclusive)
            end_date: End of period (exclusive)

        Returns:
            Dictionary containing:
            - runs_below_target: Number of runs faster than target pace
            - total_runs: Total runs in period
            - pct_below_target: Percentage meeting goal (0-100)
            - best_pace: Fastest pace achieved in period (or None)

        Business Logic:
            - Only counts predicted_activity_type == 'real_run'
            - Lower pace number = faster = better
            - Returns 0% if no runs in period
        """
        # Filter to date range
        period_df = self.df[
            (self.df['workout_date'] >= start_date) &
            (self.df['workout_date'] < end_date)
        ].copy()

        # Filter to runs only
        runs_df = period_df[period_df['predicted_activity_type'] == 'real_run'].copy()

        if runs_df.empty:
            return {
                'runs_below_target': 0,
                'total_runs': 0,
                'pct_below_target': 0.0,
                'best_pace': None
            }

        # Check if avg_pace column exists
        if 'avg_pace' not in runs_df.columns:
            return {
                'runs_below_target': 0,
                'total_runs': len(runs_df),
                'pct_below_target': 0.0,
                'best_pace': None,
                'error': 'avg_pace column not available'
            }

        # Filter out invalid pace values
        valid_runs = runs_df[runs_df['avg_pace'].notna() & (runs_df['avg_pace'] > 0)].copy()

        if valid_runs.empty:
            return {
                'runs_below_target': 0,
                'total_runs': len(runs_df),
                'pct_below_target': 0.0,
                'best_pace': None
            }

        # Count runs below (faster than) target pace
        runs_below = (valid_runs['avg_pace'] < target_pace).sum()
        total_runs = len(valid_runs)
        pct_below = (runs_below / total_runs * 100) if total_runs > 0 else 0.0
        best_pace = valid_runs['avg_pace'].min()

        return {
            'runs_below_target': int(runs_below),
            'total_runs': int(total_runs),
            'pct_below_target': float(pct_below),
            'best_pace': float(best_pace) if pd.notna(best_pace) else None
        }
