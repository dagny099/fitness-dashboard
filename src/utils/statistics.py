"""Statistical utilities for fitness intelligence analysis."""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional, Any
from scipy import stats
from scipy.signal import find_peaks
import warnings

class TrendAnalysis:
    """Advanced trend analysis for fitness metrics."""
    
    @staticmethod
    def calculate_trend(values: pd.Series, periods: int = 30) -> Dict[str, Any]:
        """
        Calculate trend analysis with confidence intervals.
        
        Args:
            values: Time series data
            periods: Number of periods for trend calculation
            
        Returns:
            Dictionary with trend statistics
        """
        if len(values) < 3:
            return {
                'trend_direction': 'insufficient_data',
                'trend_strength': 0,
                'confidence': 0,
                'slope': 0,
                'r_squared': 0
            }
        
        # Remove NaN values
        clean_data = values.dropna()
        if len(clean_data) < 3:
            return {
                'trend_direction': 'insufficient_data',
                'trend_strength': 0,
                'confidence': 0,
                'slope': 0,
                'r_squared': 0
            }
        
        # Take last N periods if dataset is large
        if len(clean_data) > periods:
            clean_data = clean_data.tail(periods)
        
        x = np.arange(len(clean_data))
        y = clean_data.values
        
        try:
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Calculate trend direction and strength
            trend_direction = 'ascending' if slope > 0 else 'descending' if slope < 0 else 'stable'
            trend_strength = abs(r_value)  # Correlation coefficient as strength
            confidence = max(0, min(100, (1 - p_value) * 100))
            
            return {
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'confidence': confidence,
                'slope': slope,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'std_error': std_err
            }
        
        except Exception as e:
            return {
                'trend_direction': 'error',
                'trend_strength': 0,
                'confidence': 0,
                'slope': 0,
                'r_squared': 0,
                'error': str(e)
            }
    
    @staticmethod
    def forecast_values(values: pd.Series, periods: int = 14, method: str = 'linear') -> Dict[str, Any]:
        """
        Forecast future values based on historical trends.
        
        Args:
            values: Historical data
            periods: Number of periods to forecast
            method: Forecasting method ('linear', 'moving_average')
            
        Returns:
            Dictionary with forecasted values and confidence intervals
        """
        clean_data = values.dropna()
        if len(clean_data) < 5:
            return {
                'forecast': [],
                'confidence_upper': [],
                'confidence_lower': [],
                'method': method,
                'error': 'Insufficient data for forecasting'
            }
        
        try:
            if method == 'linear':
                # Linear trend extrapolation
                x = np.arange(len(clean_data))
                y = clean_data.values
                
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                # Generate forecast
                future_x = np.arange(len(clean_data), len(clean_data) + periods)
                forecast = slope * future_x + intercept
                
                # Calculate confidence intervals (rough approximation)
                residual_std = np.std(y - (slope * x + intercept))
                margin_of_error = 1.96 * residual_std  # 95% confidence interval
                
                confidence_upper = forecast + margin_of_error
                confidence_lower = forecast - margin_of_error
                
            elif method == 'moving_average':
                # Simple moving average
                window = min(7, len(clean_data) // 2)
                recent_avg = clean_data.tail(window).mean()
                recent_std = clean_data.tail(window).std()
                
                forecast = np.full(periods, recent_avg)
                confidence_upper = forecast + 1.96 * recent_std
                confidence_lower = forecast - 1.96 * recent_std
            
            return {
                'forecast': forecast.tolist(),
                'confidence_upper': confidence_upper.tolist(),
                'confidence_lower': confidence_lower.tolist(),
                'method': method,
                'confidence_score': min(100, max(0, (r_value ** 2) * 100)) if method == 'linear' else 70
            }
        
        except Exception as e:
            return {
                'forecast': [],
                'confidence_upper': [],
                'confidence_lower': [],
                'method': method,
                'error': str(e)
            }

class AnomalyDetection:
    """Anomaly detection for workout data."""
    
    @staticmethod
    def detect_outliers(values: pd.Series, method: str = 'iqr', sensitivity: float = 1.5) -> Dict[str, Any]:
        """
        Detect anomalies in workout data.
        
        Args:
            values: Data series
            method: Detection method ('iqr', 'zscore', 'modified_zscore')
            sensitivity: Sensitivity multiplier
            
        Returns:
            Dictionary with anomaly information
        """
        clean_data = values.dropna()
        if len(clean_data) < 10:
            return {
                'outliers': [],
                'outlier_indices': [],
                'method': method,
                'total_outliers': 0,
                'outlier_percentage': 0
            }
        
        try:
            if method == 'iqr':
                Q1 = clean_data.quantile(0.25)
                Q3 = clean_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - sensitivity * IQR
                upper_bound = Q3 + sensitivity * IQR
                
                outlier_mask = (clean_data < lower_bound) | (clean_data > upper_bound)
                
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(clean_data))
                outlier_mask = z_scores > sensitivity
                
            elif method == 'modified_zscore':
                median = np.median(clean_data)
                mad = np.median(np.abs(clean_data - median))
                modified_z_scores = 0.6745 * (clean_data - median) / mad
                outlier_mask = np.abs(modified_z_scores) > sensitivity
            
            outliers = clean_data[outlier_mask]
            outlier_indices = outliers.index.tolist()
            
            return {
                'outliers': outliers.tolist(),
                'outlier_indices': outlier_indices,
                'method': method,
                'total_outliers': len(outliers),
                'outlier_percentage': (len(outliers) / len(clean_data)) * 100,
                'outlier_threshold_lower': lower_bound if method == 'iqr' else None,
                'outlier_threshold_upper': upper_bound if method == 'iqr' else None
            }
        
        except Exception as e:
            return {
                'outliers': [],
                'outlier_indices': [],
                'method': method,
                'total_outliers': 0,
                'outlier_percentage': 0,
                'error': str(e)
            }
    
    @staticmethod
    def detect_performance_anomalies(df: pd.DataFrame, metric: str = 'pace', 
                                   window: int = 30) -> Dict[str, Any]:
        """
        Detect performance anomalies relative to recent performance.
        
        Args:
            df: Workout dataframe with datetime index
            metric: Metric to analyze
            window: Rolling window for baseline calculation
            
        Returns:
            Dictionary with anomaly analysis
        """
        if metric not in df.columns:
            return {'error': f'Metric {metric} not found in dataframe'}
        
        try:
            # Calculate rolling statistics
            df = df.sort_values('workout_date')
            rolling_mean = df[metric].rolling(window=window, min_periods=5).mean()
            rolling_std = df[metric].rolling(window=window, min_periods=5).std()
            
            # Calculate z-scores relative to rolling baseline
            z_scores = (df[metric] - rolling_mean) / rolling_std
            
            # Detect anomalies (more than 2 standard deviations)
            anomaly_mask = np.abs(z_scores) > 2
            anomalies = df[anomaly_mask].copy()
            
            # Classify anomaly types
            anomalies['anomaly_type'] = z_scores[anomaly_mask].apply(
                lambda x: 'positive_anomaly' if x > 0 else 'negative_anomaly'
            )
            anomalies['anomaly_severity'] = np.abs(z_scores[anomaly_mask])
            
            return {
                'anomalies': anomalies.to_dict('records'),
                'total_anomalies': len(anomalies),
                'recent_anomalies': len(anomalies[anomalies['workout_date'] >= 
                                                df['workout_date'].max() - pd.Timedelta(days=30)]),
                'anomaly_rate': len(anomalies) / len(df) * 100,
                'metric_analyzed': metric
            }
        
        except Exception as e:
            return {'error': str(e)}

class PerformanceMetrics:
    """Advanced performance metrics calculation."""
    
    @staticmethod
    def calculate_consistency_score(values: pd.Series, method: str = 'cv') -> float:
        """
        Calculate consistency score for a metric.
        
        Args:
            values: Metric values
            method: Calculation method ('cv', 'mad', 'percentile_range')
            
        Returns:
            Consistency score (0-100, higher is more consistent)
        """
        clean_data = values.dropna()
        if len(clean_data) < 3:
            return 0.0
        
        try:
            if method == 'cv':
                # Coefficient of variation (inverted for consistency)
                cv = np.std(clean_data) / np.mean(clean_data)
                consistency = max(0, 100 - (cv * 100))
                
            elif method == 'mad':
                # Mean absolute deviation (inverted and scaled)
                mad = np.mean(np.abs(clean_data - np.mean(clean_data)))
                consistency = max(0, 100 - (mad / np.mean(clean_data) * 100))
                
            elif method == 'percentile_range':
                # Interpercentile range (inverted and scaled)
                p25 = np.percentile(clean_data, 25)
                p75 = np.percentile(clean_data, 75)
                ipr = (p75 - p25) / np.median(clean_data)
                consistency = max(0, 100 - (ipr * 100))
            
            return min(100, max(0, consistency))
        
        except Exception:
            return 0.0
    
    @staticmethod
    def calculate_improvement_rate(values: pd.Series, periods: int = 90) -> Dict[str, float]:
        """
        Calculate improvement rate over specified periods.
        
        Args:
            values: Time series values
            periods: Number of recent periods to analyze
            
        Returns:
            Dictionary with improvement metrics
        """
        clean_data = values.dropna()
        if len(clean_data) < 10:
            return {'improvement_rate': 0, 'improvement_confidence': 0}
        
        try:
            # Take recent periods
            recent_data = clean_data.tail(min(periods, len(clean_data)))
            
            # Calculate linear trend
            x = np.arange(len(recent_data))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, recent_data.values)
            
            # Convert slope to percentage improvement rate
            baseline_value = recent_data.iloc[0] if len(recent_data) > 0 else recent_data.mean()
            improvement_rate = (slope / baseline_value) * 100 if baseline_value != 0 else 0
            
            # Confidence based on R-squared and p-value
            confidence = (r_value ** 2) * (1 - p_value) * 100
            
            return {
                'improvement_rate': improvement_rate,
                'improvement_confidence': min(100, max(0, confidence)),
                'trend_strength': abs(r_value),
                'is_improving': slope > 0
            }
        
        except Exception:
            return {'improvement_rate': 0, 'improvement_confidence': 0}
    
    @staticmethod
    def detect_plateaus(values: pd.Series, min_length: int = 14, threshold: float = 0.05) -> List[Dict[str, Any]]:
        """
        Detect performance plateaus in time series data.
        
        Args:
            values: Time series data
            min_length: Minimum plateau length
            threshold: Maximum acceptable change rate for plateau
            
        Returns:
            List of detected plateaus
        """
        clean_data = values.dropna()
        if len(clean_data) < min_length * 2:
            return []
        
        try:
            plateaus = []
            
            # Calculate rolling change rate
            rolling_change = clean_data.rolling(window=min_length).apply(
                lambda x: abs((x.iloc[-1] - x.iloc[0]) / x.iloc[0]) if x.iloc[0] != 0 else 0
            )
            
            # Find periods with low change rate
            plateau_mask = rolling_change < threshold
            
            # Group consecutive plateau periods
            plateau_groups = []
            current_group = []
            
            for idx, is_plateau in plateau_mask.items():
                if is_plateau:
                    current_group.append(idx)
                else:
                    if len(current_group) >= min_length:
                        plateau_groups.append(current_group)
                    current_group = []
            
            # Process last group
            if len(current_group) >= min_length:
                plateau_groups.append(current_group)
            
            # Create plateau information
            for group in plateau_groups:
                start_idx = group[0]
                end_idx = group[-1]
                duration = len(group)
                
                plateau_data = clean_data.loc[start_idx:end_idx]
                avg_value = plateau_data.mean()
                std_value = plateau_data.std()
                
                plateaus.append({
                    'start_date': start_idx,
                    'end_date': end_idx,
                    'duration_days': duration,
                    'average_value': avg_value,
                    'stability': 100 - (std_value / avg_value * 100) if avg_value != 0 else 0,
                    'plateau_level': 'high' if avg_value > clean_data.median() else 'low'
                })
            
            return plateaus
        
        except Exception:
            return []

class StatisticalInsights:
    """Generate intelligent insights from statistical analysis."""
    
    @staticmethod
    def generate_trend_insight(trend_data: Dict[str, Any], metric_name: str) -> str:
        """Generate human-readable insight from trend analysis."""
        if trend_data.get('trend_direction') == 'insufficient_data':
            return f"Need more {metric_name} data to identify trends"
        
        direction = trend_data['trend_direction']
        confidence = trend_data['confidence']
        strength = trend_data['trend_strength']
        
        if confidence < 30:
            return f"Your {metric_name} shows no clear trend pattern"
        
        confidence_text = "high confidence" if confidence > 70 else "moderate confidence" if confidence > 50 else "low confidence"
        strength_text = "strong" if strength > 0.7 else "moderate" if strength > 0.4 else "weak"
        
        if direction == 'ascending':
            return f"Your {metric_name} is improving with {strength_text} {direction} trend ({confidence_text})"
        elif direction == 'descending':
            return f"Your {metric_name} shows {strength_text} declining trend ({confidence_text})"
        else:
            return f"Your {metric_name} remains stable with {strength_text} consistency"
    
    @staticmethod
    def generate_anomaly_insight(anomaly_data: Dict[str, Any], metric_name: str) -> List[str]:
        """Generate insights from anomaly analysis."""
        insights = []
        
        total_anomalies = anomaly_data.get('total_anomalies', 0)
        anomaly_rate = anomaly_data.get('anomaly_percentage', 0)
        
        if total_anomalies == 0:
            insights.append(f"Your {metric_name} shows consistent performance with no significant outliers")
        elif anomaly_rate > 10:
            insights.append(f"Your {metric_name} has high variability with {total_anomalies} unusual workouts ({anomaly_rate:.1f}%)")
        elif anomaly_rate > 5:
            insights.append(f"Your {metric_name} shows some variability with {total_anomalies} notable workouts")
        else:
            insights.append(f"Your {metric_name} is generally consistent with only {total_anomalies} exceptional workouts")
        
        return insights
    
    @staticmethod
    def generate_performance_insight(improvement_data: Dict[str, Any], metric_name: str) -> str:
        """Generate insight from improvement analysis."""
        rate = improvement_data.get('improvement_rate', 0)
        confidence = improvement_data.get('improvement_confidence', 0)
        is_improving = improvement_data.get('is_improving', False)
        
        if confidence < 30:
            return f"Your {metric_name} shows no clear improvement pattern"
        
        if is_improving and rate > 1:
            return f"Your {metric_name} is improving at {rate:.1f}% rate (confidence: {confidence:.0f}%)"
        elif is_improving and rate > 0.1:
            return f"Your {metric_name} shows steady improvement at {rate:.1f}% rate"
        elif not is_improving and rate < -1:
            return f"Your {metric_name} is declining at {abs(rate):.1f}% rate - consider recovery focus"
        else:
            return f"Your {metric_name} remains stable with minimal change"