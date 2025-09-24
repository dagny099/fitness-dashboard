"""Main intelligence service for fitness AI analysis."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
import logging
warnings.filterwarnings('ignore', category=FutureWarning)

# Configure logging for intelligence service
logger = logging.getLogger(__name__)

from utils.statistics import TrendAnalysis, AnomalyDetection, PerformanceMetrics, StatisticalInsights
from utils.consistency_analyzer import ConsistencyAnalyzer
from services.database_service import DatabaseService
from config.app import app_config, CLASSIFICATION_DEFAULTS
from utils.data_filters import filter_workouts_by_date
from ml.model_manager import model_manager

class FitnessIntelligenceService:
    """Main service for fitness AI analysis and insights generation."""
    
    def __init__(self, db_service: Optional[DatabaseService] = None):
        """Initialize intelligence service."""
        self.db_service = db_service or DatabaseService()
        self._cached_data = None
        self._cache_timestamp = None
        self._cache_duration = timedelta(minutes=10)  # Cache for 10 minutes
        self._classification_cache = {}  # Cache for classification results

    def _get_era_based_default(self, workout_date: datetime) -> str:
        """
        Get default classification based on era (pre/post Choco Effect date).

        Args:
            workout_date: Date of the workout to classify

        Returns:
            str: Default classification based on era
                - Pre-Choco Era: 'real_run' (running-focused period)
                - Post-Choco Era: 'pup_walk' (walking/dog-walking period)

        Business Logic:
            The Choco Effect represents a significant behavioral transition from
            running-focused activities to walking/dog-walking activities. This
            method leverages years of training data patterns to provide intelligent
            defaults when machine learning classification is not possible.
        """
        choco_effect_date = app_config.choco_effect_date

        if workout_date < choco_effect_date:
            return CLASSIFICATION_DEFAULTS["pre_choco_era_default"]
        else:
            return CLASSIFICATION_DEFAULTS["post_choco_era_default"]
    
    def _load_workout_data(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load workout data with caching."""
        now = datetime.now()
        
        # Use cache if available and not expired
        if (self._cached_data is not None and 
            self._cache_timestamp is not None and 
            not force_refresh and
            now - self._cache_timestamp < self._cache_duration):
            return self._cached_data.copy()
        
        try:
            query = """
            SELECT workout_date, activity_type, kcal_burned, distance_mi, 
                   duration_sec, avg_pace, max_pace, steps
            FROM workout_summary 
            ORDER BY workout_date DESC
            """
            
            with self.db_service.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                cursor.close()
                
                if rows:
                    df = pd.DataFrame(rows)
                    df['duration_min'] = (df['duration_sec'] / 60).round(1)
                    
                    # Apply workout classification using new ML architecture
                    df = model_manager.classify_workouts(df)
                    
                    # Cache the data
                    self._cached_data = df.copy()
                    self._cache_timestamp = now
                    
                    return df
                else:
                    return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Error loading workout data: {e}")
            return pd.DataFrame()
    
    def classify_workout_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify workouts using the new persistent ML model architecture.

        This method now delegates to the ModelManager, which handles:
        - Training on full historical dataset
        - Persistent model storage and loading
        - Era-based fallbacks when appropriate

        Args:
            df: DataFrame with workout data

        Returns:
            DataFrame with added classification columns
        """
        return model_manager.classify_workouts(df)

    def ensure_model_trained(self) -> Dict[str, Any]:
        """
        Ensure that a trained model is available, training one if necessary.

        Returns:
            Dict with model status and training results
        """
        if model_manager.is_model_available():
            model_stats = model_manager.get_model_stats()
            return {
                'model_ready': True,
                'message': 'Model already trained and ready',
                'model_info': model_stats['model_summary']
            }
        else:
            logger.info("No trained model found, initiating training on full historical dataset...")
            training_result = model_manager.train_new_model()

            if training_result['success']:
                return {
                    'model_ready': True,
                    'message': 'Model trained successfully on full historical dataset',
                    'training_result': training_result
                }
            else:
                return {
                    'model_ready': False,
                    'message': f"Model training failed: {training_result['message']}",
                    'error': training_result.get('error', 'Unknown error')
                }

    def get_model_status(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the current ML model status.

        Returns:
            Dict with model availability, performance, and metadata
        """
        return model_manager.get_model_stats()

    def retrain_model(self) -> Dict[str, Any]:
        """
        Force retrain the model on full historical dataset.

        Returns:
            Dict with retraining results
        """
        logger.info("Forcing model retraining...")
        return model_manager.train_new_model(force_retrain=True)

    def get_classification_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for workout classifications.
        
        Args:
            df: DataFrame with classification results
            
        Returns:
            Dictionary with classification summary statistics
        """
        if 'predicted_activity_type' not in df.columns:
            return {'error': 'No classification data available'}
        
        try:
            summary = {}
            
            # Classification distribution
            type_counts = df['predicted_activity_type'].value_counts()
            total_classified = len(df[df['predicted_activity_type'] != 'unknown'])
            
            summary['classification_distribution'] = type_counts.to_dict()
            summary['classification_rate'] = (total_classified / len(df)) * 100 if len(df) > 0 else 0
            
            # Average confidence by type
            conf_by_type = df[df['predicted_activity_type'] != 'unknown'].groupby(
                'predicted_activity_type'
            )['classification_confidence'].agg(['mean', 'count'])
            
            summary['confidence_by_type'] = conf_by_type.to_dict()
            
            # Performance stats by type
            if total_classified > 0:
                perf_stats = df[df['predicted_activity_type'] != 'unknown'].groupby(
                    'predicted_activity_type'
                ).agg({
                    'avg_pace': ['mean', 'std'],
                    'distance_mi': ['mean', 'std'], 
                    'duration_sec': ['mean', 'std']
                }).round(2)
                
                summary['performance_by_type'] = perf_stats.to_dict()
            
            return summary
            
        except Exception as e:
            return {'error': f'Error generating classification summary: {str(e)}'}
    
    def generate_daily_intelligence_brief(self, days_lookback: int = 30, activity_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive daily intelligence brief.

        Args:
            days_lookback (int): Number of days back from current date to analyze
            activity_filter (str, optional): Filter by specific activity type

        Returns:
            dict: Intelligence brief with analysis results and metadata

        Business Logic:
            - Uses current date as reference point for "days back" calculations
            - Leverages shared date filtering utility for consistency across app
            - Includes both recent period analysis and full dataset context
        """
        try:
            # Ensure ML model is trained before proceeding
            model_status = self.ensure_model_trained()
            if not model_status['model_ready']:
                logger.warning(f"Model not ready: {model_status['message']}")
                # Continue with era-based classification as fallback

            df = self._load_workout_data()
            if df.empty:
                return {'error': 'No workout data available'}

            # Use shared filtering utility for consistency across the application
            recent_df, filter_metadata = filter_workouts_by_date(df, days_lookback=days_lookback)

            brief = {
                'generated_at': datetime.now().isoformat(),
                'analysis_period': f"Last {days_lookback} days",
                'date_range': {
                    'start_date': filter_metadata['start_date'].isoformat() if filter_metadata['start_date'] else None,
                    'end_date': filter_metadata['end_date'].isoformat() if filter_metadata['end_date'] else None,
                    'days_in_range': filter_metadata['date_range_days'],
                    'filter_method': filter_metadata['filter_method_used']
                },
                'total_workouts_analyzed': len(df),
                'recent_workouts_analyzed': len(recent_df)
            }
            
            # Core intelligence sections
            brief['classification_intelligence'] = self._analyze_classification_intelligence(recent_df)
            brief['performance_intelligence'] = self._analyze_performance_intelligence(recent_df, df)
            brief['consistency_intelligence'] = self._analyze_consistency_intelligence(recent_df)
            brief['anomaly_intelligence'] = self._analyze_anomaly_intelligence(recent_df)
            brief['predictive_intelligence'] = self._analyze_predictive_intelligence(df)
            brief['recommendations'] = self._generate_ai_recommendations(recent_df, df)
            brief['key_insights'] = self._generate_key_insights(recent_df, df)
            
            return brief
        
        except Exception as e:
            return {'error': f'Failed to generate intelligence brief: {str(e)}'}
    
    def _analyze_classification_intelligence(self, recent_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze workout classification patterns and accuracy."""
        try:
            if 'predicted_activity_type' not in recent_df.columns:
                return {'error': 'Classification data not available'}
            
            summary = self.get_classification_summary(recent_df)
            
            # Add specific insights about classification patterns
            intelligence = summary.copy()

            # Activity type preferences in recent period
            activity_counts = recent_df['predicted_activity_type'].value_counts()
            total_classified = len(recent_df[recent_df['predicted_activity_type'] != 'unknown'])

            # Include the classified workouts data for UI consistency
            intelligence['classified_workouts'] = recent_df

            # Create summary statistics for UI display
            intelligence['summary'] = activity_counts.to_dict()
            
            if total_classified > 0:
                primary_activity = activity_counts.index[0]
                primary_percentage = (activity_counts.iloc[0] / total_classified) * 100
                
                intelligence['primary_activity'] = {
                    'type': primary_activity,
                    'percentage': primary_percentage,
                    'count': activity_counts.iloc[0]
                }
                
                # Activity diversity score
                diversity_score = (len(activity_counts) - 1) / 3 * 100  # Scale 0-100
                intelligence['activity_diversity_score'] = min(100, diversity_score)
            
            return intelligence
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_performance_intelligence(self, recent_df: pd.DataFrame, 
                                        full_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance trends and metrics."""
        try:
            intelligence = {}
            
            # Key metrics analysis
            metrics = ['kcal_burned', 'distance_mi', 'duration_min', 'avg_pace']
            
            for metric in metrics:
                if metric in recent_df.columns and recent_df[metric].notna().sum() > 0:
                    # Trend analysis
                    trend_data = TrendAnalysis.calculate_trend(recent_df[metric])
                    
                    # Improvement analysis
                    improvement_data = PerformanceMetrics.calculate_improvement_rate(
                        recent_df[metric], periods=len(recent_df)
                    )
                    
                    intelligence[metric] = {
                        'trend': trend_data,
                        'improvement': improvement_data,
                        'current_average': recent_df[metric].mean(),
                        'historical_average': full_df[metric].mean(),
                        'recent_best': recent_df[metric].max(),
                        'recent_consistency': PerformanceMetrics.calculate_consistency_score(recent_df[metric])
                    }
            
            return intelligence
        
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_consistency_intelligence(self, recent_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze workout consistency patterns."""
        try:
            analyzer = ConsistencyAnalyzer(recent_df)
            
            consistency_score = analyzer.calculate_consistency_score()
            patterns = analyzer.analyze_workout_patterns()
            timing_analysis = analyzer.calculate_optimal_workout_timing()
            
            return {
                'consistency_score': consistency_score,
                'workout_patterns': patterns,
                'optimal_timing': timing_analysis,
                'consistency_insights': analyzer.generate_consistency_insights()
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_anomaly_intelligence(self, recent_df: pd.DataFrame) -> Dict[str, Any]:
        """Detect and analyze workout anomalies."""
        try:
            anomaly_data = {}
            
            # Analyze anomalies in key metrics
            metrics = ['kcal_burned', 'distance_mi', 'duration_min']
            
            for metric in metrics:
                if metric in recent_df.columns and recent_df[metric].notna().sum() > 0:
                    # Anomaly detection now works with small samples since we have historical context
                    anomalies = AnomalyDetection.detect_performance_anomalies(
                        recent_df, metric=metric, window=min(14, max(1, len(recent_df)//2))
                    )
                    anomaly_data[metric] = anomalies
            
            # Overall anomaly summary
            total_anomalies = sum(
                data.get('total_anomalies', 0) 
                for data in anomaly_data.values() 
                if isinstance(data, dict)
            )
            
            anomaly_data['summary'] = {
                'total_anomalies_detected': total_anomalies,
                'anomaly_rate': (total_anomalies / len(recent_df) * 100) if len(recent_df) > 0 else 0,
                'recent_anomalies': sum(
                    data.get('recent_anomalies', 0) 
                    for data in anomaly_data.values() 
                    if isinstance(data, dict)
                )
            }
            
            return anomaly_data
        
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_predictive_intelligence(self, full_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictive analytics and forecasts."""
        try:
            predictions = {}
            
            # Performance forecasting for key metrics
            metrics = ['kcal_burned', 'distance_mi', 'duration_min']
            
            for metric in metrics:
                if metric in full_df.columns and full_df[metric].notna().sum() > 10:
                    # 2-week forecast
                    forecast_data = TrendAnalysis.forecast_values(
                        full_df[metric].tail(90), periods=14, method='linear'
                    )
                    
                    # Plateau detection
                    plateaus = PerformanceMetrics.detect_plateaus(
                        full_df[metric], min_length=14, threshold=0.05
                    )
                    
                    predictions[metric] = {
                        'forecast': forecast_data,
                        'plateau_analysis': {
                            'current_plateaus': len([p for p in plateaus 
                                                   if p['end_date'] >= full_df[metric].index[-30]]),
                            'historical_plateaus': len(plateaus),
                            'longest_plateau': max([p['duration_days'] for p in plateaus], default=0)
                        }
                    }
            
            # Consistency trajectory prediction
            recent_consistency = []
            analyzer = ConsistencyAnalyzer(full_df)
            
            # Calculate consistency over rolling 30-day periods
            for i in range(max(0, len(full_df) - 180), len(full_df), 15):
                window_df = full_df.iloc[max(0, i-30):i+30]
                if len(window_df) > 5:
                    temp_analyzer = ConsistencyAnalyzer(window_df)
                    score_data = temp_analyzer.calculate_consistency_score()
                    recent_consistency.append(score_data.get('consistency_score', 0))
            
            if len(recent_consistency) > 3:
                consistency_trend = TrendAnalysis.calculate_trend(pd.Series(recent_consistency))
                predictions['consistency_trajectory'] = consistency_trend
            
            return predictions
        
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_ai_recommendations(self, recent_df: pd.DataFrame, 
                                   full_df: pd.DataFrame) -> List[str]:
        """Generate AI-style recommendations based on analysis."""
        try:
            recommendations = []
            
            # Consistency-based recommendations
            analyzer = ConsistencyAnalyzer(recent_df)
            consistency_data = analyzer.calculate_consistency_score()
            consistency_score = consistency_data.get('consistency_score', 0)
            
            if consistency_score < 50:
                recommendations.append(
                    "🎯 Focus Priority: Your consistency score is low. "
                    "Target 3 workouts per week for 2 weeks to build momentum."
                )
            elif consistency_score < 75:
                recommendations.append(
                    "📈 Optimization Target: Good consistency foundation detected. "
                    "Add one extra workout per week to reach high-consistency zone."
                )
            else:
                recommendations.append(
                    "🔥 Maintain Excellence: Your consistency is in the top tier. "
                    "Focus on performance optimization within current routine."
                )
            
            # Performance-based recommendations
            if 'kcal_burned' in recent_df.columns:
                calorie_trend = TrendAnalysis.calculate_trend(recent_df['kcal_burned'])
                if calorie_trend['trend_direction'] == 'descending' and calorie_trend['confidence'] > 60:
                    recommendations.append(
                        "⚠️ Performance Alert: Calorie burn trending down. "
                        "Consider increasing workout intensity or duration."
                    )
                elif calorie_trend['trend_direction'] == 'ascending' and calorie_trend['confidence'] > 70:
                    recommendations.append(
                        "🚀 Performance Momentum: Calorie burn is improving. "
                        "Continue current trajectory - you're in a growth phase."
                    )
            
            # Timing optimization recommendations
            timing_data = analyzer.calculate_optimal_workout_timing()
            if 'best_day_for_calories' in timing_data:
                best_day = timing_data['best_day_for_calories']
                recommendations.append(
                    f"📅 Timing Intelligence: Your best performance day is {best_day}. "
                    f"Schedule challenging workouts then for optimal results."
                )
            
            # Activity variety recommendations
            if 'activity_type' in recent_df.columns:
                activity_counts = recent_df['activity_type'].value_counts()
                if len(activity_counts) == 1:
                    recommendations.append(
                        "🌟 Diversification Opportunity: You're focused on one activity. "
                        "Adding variety can prevent plateaus and reduce injury risk."
                    )
                elif len(activity_counts) >= 3:
                    recommendations.append(
                        "💪 Great Variety: Your diverse activity mix is optimal for "
                        "balanced fitness and sustained motivation."
                    )
            
            # Ensure we always have at least one recommendation
            if not recommendations:
                recommendations.append(
                    "📊 Data Collection Phase: Building your fitness intelligence profile. "
                    "Continue consistent tracking for personalized insights."
                )
            
            return recommendations[:4]  # Limit to top 4 recommendations
        
        except Exception as e:
            return [f"Error generating recommendations: {str(e)}"]
    
    def _generate_key_insights(self, recent_df: pd.DataFrame, 
                             full_df: pd.DataFrame) -> List[str]:
        """Generate key insights from the analysis."""
        try:
            insights = []
            
            # Performance insights
            if 'kcal_burned' in recent_df.columns and len(recent_df) >= 5:
                recent_avg = recent_df['kcal_burned'].mean()
                historical_avg = full_df['kcal_burned'].mean()
                
                change_pct = ((recent_avg - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0
                
                if abs(change_pct) > 10:
                    direction = "higher" if change_pct > 0 else "lower"
                    insights.append(
                        f"📊 Performance Shift: Recent calorie burn is {abs(change_pct):.1f}% "
                        f"{direction} than your historical average"
                    )
            
            # Frequency insights
            recent_days = (recent_df['workout_date'].max() - recent_df['workout_date'].min()).days + 1
            recent_frequency = len(recent_df) / (recent_days / 7) if recent_days > 0 else 0
            
            if recent_frequency >= 4:
                insights.append(f"🔥 High Activity: You're averaging {recent_frequency:.1f} workouts per week")
            elif recent_frequency >= 2:
                insights.append(f"💪 Steady Pace: Maintaining {recent_frequency:.1f} workouts per week")
            else:
                insights.append(f"📈 Building Phase: {recent_frequency:.1f} workouts per week - room to grow")
            
            # Activity classification insights (enhanced)
            if 'predicted_activity_type' in recent_df.columns:
                classified_df = recent_df[recent_df['predicted_activity_type'].isin(['real_run', 'pup_walk', 'mixed'])]
                
                if len(classified_df) > 0:
                    activity_counts = classified_df['predicted_activity_type'].value_counts()
                    top_activity = activity_counts.index[0]
                    activity_pct = (activity_counts.iloc[0] / len(classified_df)) * 100
                    
                    # Generate activity-specific insights
                    if top_activity == 'real_run':
                        run_pace = classified_df[classified_df['predicted_activity_type'] == 'real_run']['avg_pace'].mean()
                        insights.append(f"🏃 Running Focus: {activity_pct:.0f}% real runs averaging {run_pace:.1f} min/mile")
                    elif top_activity == 'pup_walk':
                        walk_pace = classified_df[classified_df['predicted_activity_type'] == 'pup_walk']['avg_pace'].mean()
                        insights.append(f"🐕 Walking Dominant: {activity_pct:.0f}% choco adventures averaging {walk_pace:.1f} min/mile")
                    else:
                        insights.append(f"⚖️ Mixed Activity: {activity_pct:.0f}% mixed workouts - good training variety")
                    
                    # Add secondary activity insight if significant
                    if len(activity_counts) > 1 and activity_counts.iloc[1] / len(classified_df) > 0.2:
                        second_activity = activity_counts.index[1]
                        second_pct = (activity_counts.iloc[1] / len(classified_df)) * 100
                        insights.append(f"➕ Secondary Activity: {second_pct:.0f}% {second_activity.replace('_', ' ')}")
            
            # Fallback to original activity_type if classification not available
            elif 'activity_type' in recent_df.columns:
                top_activity = recent_df['activity_type'].mode().iloc[0]
                activity_pct = (recent_df['activity_type'] == top_activity).mean() * 100
                
                if activity_pct >= 70:
                    insights.append(f"🎯 Activity Focus: {top_activity} dominates {activity_pct:.0f}% of recent workouts")
                else:
                    insights.append(f"🌟 Balanced Mix: {top_activity} leads but you maintain good variety")
            
            # Consistency insights
            analyzer = ConsistencyAnalyzer(recent_df)
            consistency_score = analyzer.calculate_consistency_score().get('consistency_score', 0)
            
            if consistency_score >= 80:
                insights.append(f"🏆 Consistency Master: {consistency_score:.0f}/100 consistency score")
            elif consistency_score >= 60:
                insights.append(f"📊 Good Rhythm: {consistency_score:.0f}/100 consistency - trending positive")
            else:
                insights.append(f"🎯 Focus Area: {consistency_score:.0f}/100 consistency - opportunity for improvement")
            
            return insights[:4]  # Limit to top 4 insights
        
        except Exception as e:
            return [f"Error generating insights: {str(e)}"]
    
    def analyze_specific_metric(self, metric: str, periods: int = 90) -> Dict[str, Any]:
        """Deep dive analysis of a specific fitness metric."""
        try:
            df = self._load_workout_data()
            if df.empty or metric not in df.columns:
                return {'error': f'Metric {metric} not available in data'}
            
            # Focus on recent periods
            recent_df = df.tail(periods)
            metric_data = recent_df[metric].dropna()
            
            if len(metric_data) < 5:
                return {'error': f'Insufficient data for {metric} analysis'}
            
            analysis = {
                'metric': metric,
                'analysis_period': periods,
                'data_points': len(metric_data),
                'basic_stats': {
                    'mean': metric_data.mean(),
                    'median': metric_data.median(),
                    'std': metric_data.std(),
                    'min': metric_data.min(),
                    'max': metric_data.max()
                }
            }
            
            # Advanced statistical analysis
            analysis['trend_analysis'] = TrendAnalysis.calculate_trend(metric_data)
            analysis['forecast'] = TrendAnalysis.forecast_values(metric_data, periods=14)
            analysis['anomaly_analysis'] = AnomalyDetection.detect_outliers(metric_data)
            analysis['improvement_analysis'] = PerformanceMetrics.calculate_improvement_rate(metric_data)
            analysis['plateau_analysis'] = PerformanceMetrics.detect_plateaus(metric_data)
            
            # Generate insights
            insights = []
            insights.append(StatisticalInsights.generate_trend_insight(analysis['trend_analysis'], metric))
            insights.extend(StatisticalInsights.generate_anomaly_insight(analysis['anomaly_analysis'], metric))
            insights.append(StatisticalInsights.generate_performance_insight(analysis['improvement_analysis'], metric))
            
            analysis['insights'] = insights
            
            return analysis
        
        except Exception as e:
            return {'error': f'Failed to analyze {metric}: {str(e)}'}
    
    def get_performance_summary(self, timeframe: str = '30d') -> Dict[str, Any]:
        """Get high-level performance summary for dashboard."""
        try:
            df = self._load_workout_data()
            if df.empty:
                return {'error': 'No data available'}
            
            # Parse timeframe
            if timeframe == '7d':
                days = 7
            elif timeframe == '30d':
                days = 30
            elif timeframe == '90d':
                days = 90
            else:
                days = 30
            
            end_date = df['workout_date'].max()
            start_date = end_date - pd.Timedelta(days=days)
            period_df = df[df['workout_date'] >= start_date]
            
            summary = {
                'timeframe': timeframe,
                'total_workouts': len(period_df),
                'workout_frequency': len(period_df) / (days / 7),
                'metrics': {}
            }
            
            # Calculate metrics summaries
            metrics = ['kcal_burned', 'distance_mi', 'duration_min']
            for metric in metrics:
                if metric in period_df.columns:
                    data = period_df[metric].dropna()
                    if len(data) > 0:
                        summary['metrics'][metric] = {
                            'average': data.mean(),
                            'total': data.sum(),
                            'trend': TrendAnalysis.calculate_trend(data)['trend_direction'],
                            'consistency': PerformanceMetrics.calculate_consistency_score(data)
                        }
            
            # Add intelligence score
            analyzer = ConsistencyAnalyzer(period_df)
            summary['intelligence_score'] = analyzer.calculate_consistency_score()
            
            return summary
        
        except Exception as e:
            return {'error': f'Failed to generate summary: {str(e)}'}