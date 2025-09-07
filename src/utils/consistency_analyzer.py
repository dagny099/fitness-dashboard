"""Advanced consistency analysis for fitness tracking."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from .statistics import PerformanceMetrics, TrendAnalysis

class ConsistencyAnalyzer:
    """Advanced consistency analysis and scoring system."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer with workout dataframe.
        
        Args:
            df: Workout dataframe with workout_date column
        """
        self.df = df.copy()
        if 'workout_date' in self.df.columns:
            self.df['workout_date'] = pd.to_datetime(self.df['workout_date'])
            self.df = self.df.sort_values('workout_date')
    
    def calculate_consistency_score(self, periods: int = 30) -> Dict[str, Any]:
        """
        Calculate comprehensive consistency score.
        
        Args:
            periods: Number of days to analyze for consistency
            
        Returns:
            Dictionary with consistency metrics
        """
        try:
            # Get recent period
            end_date = self.df['workout_date'].max()
            start_date = end_date - pd.Timedelta(days=periods)
            recent_df = self.df[self.df['workout_date'] >= start_date]
            
            if len(recent_df) == 0:
                return {'consistency_score': 0, 'error': 'No recent data'}
            
            # Calculate different consistency metrics
            frequency_score = self._calculate_frequency_consistency(recent_df, periods)
            timing_score = self._calculate_timing_consistency(recent_df)
            performance_score = self._calculate_performance_consistency(recent_df)
            streak_score = self._calculate_streak_metrics(recent_df)
            
            # Weighted composite score
            weights = {
                'frequency': 0.4,
                'timing': 0.2,
                'performance': 0.2,
                'streak': 0.2
            }
            
            composite_score = (
                frequency_score * weights['frequency'] +
                timing_score * weights['timing'] +
                performance_score * weights['performance'] +
                streak_score * weights['streak']
            )
            
            return {
                'consistency_score': min(100, max(0, composite_score)),
                'frequency_score': frequency_score,
                'timing_score': timing_score,
                'performance_score': performance_score,
                'streak_score': streak_score,
                'analysis_period_days': periods,
                'workouts_analyzed': len(recent_df)
            }
        
        except Exception as e:
            return {'consistency_score': 0, 'error': str(e)}
    
    def _calculate_frequency_consistency(self, df: pd.DataFrame, periods: int) -> float:
        """Calculate consistency based on workout frequency."""
        try:
            # Calculate workouts per week
            workouts_per_week = len(df) / (periods / 7)
            
            # Daily workout distribution
            df['date'] = df['workout_date'].dt.date
            daily_counts = df.groupby('date').size()
            
            # Create complete date range
            date_range = pd.date_range(
                start=df['workout_date'].min().date(),
                end=df['workout_date'].max().date(),
                freq='D'
            )
            
            # Fill missing days with 0
            daily_workout_series = pd.Series(
                index=date_range.date,
                data=[daily_counts.get(date, 0) for date in date_range.date]
            )
            
            # Calculate frequency metrics
            active_days = (daily_workout_series > 0).sum()
            active_day_percentage = (active_days / len(daily_workout_series)) * 100
            
            # Score based on activity frequency (targeting ~3-5 workouts/week)
            optimal_weekly_workouts = 4
            frequency_deviation = abs(workouts_per_week - optimal_weekly_workouts)
            frequency_score = max(0, 100 - (frequency_deviation * 15))
            
            # Bonus for high active day percentage
            consistency_bonus = active_day_percentage * 0.5
            
            return min(100, frequency_score + consistency_bonus)
        
        except Exception:
            return 0.0
    
    def _calculate_timing_consistency(self, df: pd.DataFrame) -> float:
        """Calculate consistency based on workout timing patterns."""
        try:
            if len(df) < 5:
                return 50.0  # Neutral score for insufficient data
            
            # Day of week consistency
            df['day_of_week'] = df['workout_date'].dt.dayofweek
            dow_distribution = df['day_of_week'].value_counts()
            dow_consistency = 100 - (dow_distribution.std() / dow_distribution.mean() * 100)
            
            # Inter-workout interval consistency
            df_sorted = df.sort_values('workout_date')
            intervals = df_sorted['workout_date'].diff().dt.days.dropna()
            
            if len(intervals) > 1:
                interval_cv = intervals.std() / intervals.mean()
                interval_consistency = max(0, 100 - (interval_cv * 50))
            else:
                interval_consistency = 50.0
            
            # Combine timing metrics
            timing_score = (dow_consistency * 0.4 + interval_consistency * 0.6)
            
            return min(100, max(0, timing_score))
        
        except Exception:
            return 50.0
    
    def _calculate_performance_consistency(self, df: pd.DataFrame) -> float:
        """Calculate consistency based on performance metrics."""
        try:
            consistency_scores = []
            
            # Check key performance metrics
            metrics = ['kcal_burned', 'distance_mi', 'duration_sec']
            available_metrics = [m for m in metrics if m in df.columns]
            
            for metric in available_metrics:
                if df[metric].notna().sum() > 3:
                    metric_consistency = PerformanceMetrics.calculate_consistency_score(
                        df[metric], method='cv'
                    )
                    consistency_scores.append(metric_consistency)
            
            if consistency_scores:
                return np.mean(consistency_scores)
            else:
                return 50.0
        
        except Exception:
            return 50.0
    
    def _calculate_streak_metrics(self, df: pd.DataFrame) -> float:
        """Calculate streak-based consistency metrics."""
        try:
            # Create daily workout indicator
            df['date'] = df['workout_date'].dt.date
            workout_dates = set(df['date'])
            
            # Find current and recent streaks
            end_date = df['workout_date'].max().date()
            current_streak = 0
            longest_streak = 0
            temp_streak = 0
            
            # Calculate streaks (allowing 1 day gaps for rest days)
            date_range = pd.date_range(
                start=df['workout_date'].min().date(),
                end=end_date,
                freq='D'
            )
            
            for i, date in enumerate(date_range.date):
                if date in workout_dates:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                    
                    # Update current streak if this is recent
                    if i >= len(date_range.date) - 30:  # Last 30 days
                        current_streak = temp_streak
                else:
                    temp_streak = 0
                    if i >= len(date_range.date) - 30:  # Reset current streak
                        current_streak = 0
            
            # Score based on streaks
            current_streak_score = min(50, current_streak * 5)  # Up to 50 points
            longest_streak_score = min(50, longest_streak * 2)  # Up to 50 points
            
            return current_streak_score + longest_streak_score
        
        except Exception:
            return 0.0
    
    def analyze_workout_patterns(self) -> Dict[str, Any]:
        """Analyze comprehensive workout patterns."""
        try:
            patterns = {}
            
            # Day of week analysis
            self.df['day_of_week'] = self.df['workout_date'].dt.day_name()
            dow_counts = self.df['day_of_week'].value_counts()
            patterns['preferred_days'] = dow_counts.head(3).to_dict()
            patterns['day_distribution'] = dow_counts.to_dict()
            
            # Time patterns (if hour data available)
            if 'workout_hour' in self.df.columns:
                hour_counts = self.df['workout_hour'].value_counts()
                patterns['preferred_hours'] = hour_counts.head(3).to_dict()
            
            # Monthly patterns
            self.df['month'] = self.df['workout_date'].dt.month_name()
            month_counts = self.df['month'].value_counts()
            patterns['monthly_distribution'] = month_counts.to_dict()
            
            # Activity type patterns
            if 'activity_type' in self.df.columns:
                activity_counts = self.df['activity_type'].value_counts()
                patterns['activity_preferences'] = activity_counts.to_dict()
            
            # Workout frequency patterns
            patterns['frequency_analysis'] = self._analyze_frequency_patterns()
            
            return patterns
        
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_frequency_patterns(self) -> Dict[str, Any]:
        """Analyze workout frequency patterns over time."""
        try:
            # Monthly workout counts
            monthly_counts = self.df.groupby(
                self.df['workout_date'].dt.to_period('M')
            ).size()
            
            # Calculate frequency statistics
            avg_monthly = monthly_counts.mean()
            std_monthly = monthly_counts.std()
            cv_monthly = std_monthly / avg_monthly if avg_monthly > 0 else 0
            
            # Trend analysis
            trend_data = TrendAnalysis.calculate_trend(monthly_counts)
            
            return {
                'average_monthly_workouts': avg_monthly,
                'monthly_variability': cv_monthly,
                'frequency_trend': trend_data,
                'most_active_month': monthly_counts.idxmax().strftime('%B %Y') if len(monthly_counts) > 0 else None,
                'least_active_month': monthly_counts.idxmin().strftime('%B %Y') if len(monthly_counts) > 0 else None
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def detect_consistency_phases(self) -> List[Dict[str, Any]]:
        """Detect different consistency phases in workout history."""
        try:
            phases = []
            
            # Calculate rolling 30-day consistency scores
            df_sorted = self.df.sort_values('workout_date')
            
            # Group data into 30-day windows
            window_size = 30
            for i in range(0, len(df_sorted) - window_size, window_size // 2):
                window_df = df_sorted.iloc[i:i + window_size]
                
                if len(window_df) < 5:
                    continue
                
                # Calculate metrics for this window
                start_date = window_df['workout_date'].min()
                end_date = window_df['workout_date'].max()
                workout_count = len(window_df)
                
                # Create temporary analyzer for this window
                temp_analyzer = ConsistencyAnalyzer(window_df)
                consistency_data = temp_analyzer.calculate_consistency_score(window_size)
                
                phase = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration_days': (end_date - start_date).days,
                    'workout_count': workout_count,
                    'consistency_score': consistency_data.get('consistency_score', 0),
                    'phase_type': self._classify_consistency_phase(
                        consistency_data.get('consistency_score', 0),
                        workout_count
                    )
                }
                
                phases.append(phase)
            
            return phases
        
        except Exception as e:
            return [{'error': str(e)}]
    
    def _classify_consistency_phase(self, score: float, workout_count: int) -> str:
        """Classify consistency phase based on score and workout count."""
        if score >= 80:
            return 'high_consistency'
        elif score >= 60:
            return 'moderate_consistency'
        elif score >= 40:
            return 'building_consistency'
        elif workout_count > 0:
            return 'low_consistency'
        else:
            return 'inactive_period'
    
    def generate_consistency_insights(self) -> List[str]:
        """Generate human-readable consistency insights."""
        try:
            insights = []
            
            # Overall consistency analysis
            consistency_data = self.calculate_consistency_score()
            score = consistency_data.get('consistency_score', 0)
            
            if score >= 80:
                insights.append(f"🔥 Excellent consistency! Your consistency score is {score:.0f}/100")
            elif score >= 60:
                insights.append(f"💪 Good consistency with score of {score:.0f}/100 - room for improvement")
            elif score >= 40:
                insights.append(f"📈 Building consistency at {score:.0f}/100 - you're on the right track")
            else:
                insights.append(f"🎯 Focus needed: consistency score is {score:.0f}/100")
            
            # Pattern insights
            patterns = self.analyze_workout_patterns()
            
            # Day preference insight
            if 'preferred_days' in patterns:
                top_day = list(patterns['preferred_days'].keys())[0]
                top_count = list(patterns['preferred_days'].values())[0]
                insights.append(f"📅 You're most active on {top_day}s with {top_count} workouts")
            
            # Activity preference insight
            if 'activity_preferences' in patterns:
                top_activity = list(patterns['activity_preferences'].keys())[0]
                activity_percentage = (list(patterns['activity_preferences'].values())[0] / 
                                     len(self.df)) * 100
                insights.append(f"🏃 {top_activity} is your go-to activity ({activity_percentage:.0f}% of workouts)")
            
            # Frequency insight
            freq_data = patterns.get('frequency_analysis', {})
            if 'average_monthly_workouts' in freq_data:
                avg_monthly = freq_data['average_monthly_workouts']
                insights.append(f"📊 You average {avg_monthly:.1f} workouts per month")
            
            return insights
        
        except Exception as e:
            return [f"Error generating insights: {str(e)}"]
    
    def calculate_optimal_workout_timing(self) -> Dict[str, Any]:
        """Calculate optimal workout timing based on historical performance."""
        try:
            if 'kcal_burned' not in self.df.columns or len(self.df) < 10:
                return {'error': 'Insufficient data for timing analysis'}
            
            # Day of week analysis
            self.df['day_of_week'] = self.df['workout_date'].dt.day_name()
            dow_performance = self.df.groupby('day_of_week').agg({
                'kcal_burned': ['mean', 'count'],
                'distance_mi': 'mean',
                'duration_sec': 'mean'
            }).round(2)
            
            # Find best performing days
            best_calorie_day = dow_performance[('kcal_burned', 'mean')].idxmax()
            best_distance_day = dow_performance[('distance_mi', 'mean')].idxmax()
            
            # Month analysis
            self.df['month'] = self.df['workout_date'].dt.month_name()
            month_performance = self.df.groupby('month').agg({
                'kcal_burned': ['mean', 'count']
            }).round(2)
            
            best_month = month_performance[('kcal_burned', 'mean')].idxmax()
            
            return {
                'best_day_for_calories': best_calorie_day,
                'best_day_for_distance': best_distance_day,
                'best_month': best_month,
                'day_performance_data': dow_performance.to_dict(),
                'monthly_performance_data': month_performance.to_dict()
            }
        
        except Exception as e:
            return {'error': str(e)}