"""
ML Model Manager for Fitness Classification

This module provides a complete ML model lifecycle management system for workout classification.
It implements proper model training, persistence, versioning, and application - addressing the
architectural issues in the original approach.

Key Design Principles:
- Train on full historical dataset (not recent subsets)
- Persist learned parameters for reuse
- Version models with metadata tracking
- Provide graceful fallbacks and confidence scoring
- Support model retraining and performance evaluation

Business Context:
The Choco Effect represents a behavioral transition from running to walking activities.
This system leverages years of training data to provide accurate classification even
for sparse recent periods.
"""

import os
import pickle
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

from config.app import app_config, CLASSIFICATION_DEFAULTS, ACTIVITY_TYPE_CONFIG
from services.database_service import DatabaseService
import logging

logger = logging.getLogger(__name__)


class WorkoutClassificationModel:
    """
    Persistent workout classification model with full lifecycle management.

    This class encapsulates all aspects of the ML model including training data,
    learned parameters, metadata, and performance metrics.
    """

    def __init__(self):
        """Initialize empty model structure."""
        self.model_id: Optional[str] = None
        self.created_at: Optional[datetime] = None
        self.trained_at: Optional[datetime] = None
        self.version: str = "1.0.0"

        # Core ML components
        self.kmeans: Optional[KMeans] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns: List[str] = ['avg_pace', 'distance_mi', 'duration_min']

        # Classification mapping
        self.cluster_to_activity_map: Dict[int, str] = {}
        self.activity_type_stats: Dict[str, Dict] = {}

        # Training metadata
        self.training_data_info: Dict = {}
        self.performance_metrics: Dict = {}
        self.feature_importance: Dict = {}

        # Model parameters
        self.n_clusters: int = 3
        self.random_state: int = 42
        self.confidence_threshold: float = CLASSIFICATION_DEFAULTS["min_confidence_threshold"]

    def to_dict(self) -> Dict:
        """Serialize model metadata to dictionary (excludes sklearn objects)."""
        return {
            'model_id': self.model_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'trained_at': self.trained_at.isoformat() if self.trained_at else None,
            'version': self.version,
            'feature_columns': self.feature_columns,
            'cluster_to_activity_map': self.cluster_to_activity_map,
            'activity_type_stats': self.activity_type_stats,
            'training_data_info': self.training_data_info,
            'performance_metrics': self.performance_metrics,
            'feature_importance': self.feature_importance,
            'n_clusters': self.n_clusters,
            'random_state': self.random_state,
            'confidence_threshold': self.confidence_threshold
        }

    def from_dict(self, data: Dict):
        """Load model metadata from dictionary."""
        self.model_id = data.get('model_id')
        self.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        self.trained_at = datetime.fromisoformat(data['trained_at']) if data.get('trained_at') else None
        self.version = data.get('version', '1.0.0')
        self.feature_columns = data.get('feature_columns', ['avg_pace', 'distance_mi', 'duration_min'])
        self.cluster_to_activity_map = data.get('cluster_to_activity_map', {})
        self.activity_type_stats = data.get('activity_type_stats', {})
        self.training_data_info = data.get('training_data_info', {})
        self.performance_metrics = data.get('performance_metrics', {})
        self.feature_importance = data.get('feature_importance', {})
        self.n_clusters = data.get('n_clusters', 3)
        self.random_state = data.get('random_state', 42)
        self.confidence_threshold = data.get('confidence_threshold', 0.3)

    def is_trained(self) -> bool:
        """Check if model has been trained and is ready for classification."""
        return (self.kmeans is not None and
                self.scaler is not None and
                len(self.cluster_to_activity_map) > 0)

    def get_model_summary(self) -> Dict:
        """Get human-readable summary of model state and performance."""
        if not self.is_trained():
            return {
                'status': 'untrained',
                'message': 'Model has not been trained yet'
            }

        total_training_workouts = self.training_data_info.get('total_workouts', 0)
        training_period = self.training_data_info.get('date_range', {})
        silhouette = self.performance_metrics.get('silhouette_score', 0)

        return {
            'status': 'trained',
            'model_id': self.model_id,
            'version': self.version,
            'trained_at': self.trained_at.strftime('%Y-%m-%d %H:%M:%S') if self.trained_at else 'Unknown',
            'training_workouts': total_training_workouts,
            'training_period': f"{training_period.get('start_date', '')} to {training_period.get('end_date', '')}",
            'clusters': self.n_clusters,
            'activity_types': list(self.cluster_to_activity_map.values()),
            'silhouette_score': round(silhouette, 3),
            'quality_rating': self._get_quality_rating(silhouette),
            'classification_mapping': {
                f"Cluster {k}": v for k, v in self.cluster_to_activity_map.items()
            }
        }

    def _get_quality_rating(self, silhouette_score: float) -> str:
        """Convert silhouette score to human-readable quality rating."""
        if silhouette_score >= 0.7:
            return "Excellent"
        elif silhouette_score >= 0.5:
            return "Good"
        elif silhouette_score >= 0.3:
            return "Acceptable"
        else:
            return "Needs Improvement"


class ModelManager:
    """
    Complete ML model lifecycle management for workout classification.

    Handles model training, persistence, loading, versioning, and application.
    Implements proper separation between training (full dataset) and inference
    (individual workouts or small batches).
    """

    def __init__(self, db_service: Optional[DatabaseService] = None, models_dir: str = "models"):
        """
        Initialize model manager.

        Args:
            db_service: Database service for accessing workout data
            models_dir: Directory for storing model files
        """
        self.db_service = db_service or DatabaseService()

        # Create models directory structure
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        (self.models_dir / "active").mkdir(exist_ok=True)
        (self.models_dir / "archive").mkdir(exist_ok=True)

        self.current_model: Optional[WorkoutClassificationModel] = None

        # Try to load existing active model
        self._load_active_model()

    def _load_active_model(self) -> bool:
        """
        Load the currently active model from disk.

        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        active_model_path = self.models_dir / "active" / "current_model"
        metadata_path = active_model_path.with_suffix('.json')
        sklearn_path = active_model_path.with_suffix('.pkl')

        if not (metadata_path.exists() and sklearn_path.exists()):
            logger.info("No active model found. Training will be required.")
            return False

        try:
            # Load metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            # Load sklearn objects
            with open(sklearn_path, 'rb') as f:
                sklearn_objects = pickle.load(f)

            # Reconstruct model
            self.current_model = WorkoutClassificationModel()
            self.current_model.from_dict(metadata)
            self.current_model.kmeans = sklearn_objects['kmeans']
            self.current_model.scaler = sklearn_objects['scaler']

            logger.info(f"Loaded active model: {self.current_model.model_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to load active model: {e}")
            return False

    def _save_model(self, model: WorkoutClassificationModel, archive: bool = False) -> bool:
        """
        Save model to disk with metadata and sklearn objects.

        Args:
            model: Model to save
            archive: If True, save to archive instead of active

        Returns:
            bool: True if saved successfully
        """
        try:
            if archive:
                save_dir = self.models_dir / "archive"
                filename = f"model_{model.model_id}"
            else:
                save_dir = self.models_dir / "active"
                filename = "current_model"

            metadata_path = save_dir / f"{filename}.json"
            sklearn_path = save_dir / f"{filename}.pkl"

            # Save metadata
            with open(metadata_path, 'w') as f:
                json.dump(model.to_dict(), f, indent=2)

            # Save sklearn objects
            sklearn_objects = {
                'kmeans': model.kmeans,
                'scaler': model.scaler
            }
            with open(sklearn_path, 'wb') as f:
                pickle.dump(sklearn_objects, f)

            logger.info(f"Saved model to {save_dir}/{filename}")
            return True

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def get_current_model(self) -> Optional[WorkoutClassificationModel]:
        """Get the currently active model."""
        return self.current_model

    def is_model_available(self) -> bool:
        """Check if a trained model is available for classification."""
        return self.current_model is not None and self.current_model.is_trained()

    def train_new_model(self, force_retrain: bool = False) -> Dict[str, Any]:
        """
        Train a new classification model on full historical dataset.

        This is the core method that implements proper ML training using ALL
        available data rather than recent subsets.

        Args:
            force_retrain: If True, retrain even if current model exists

        Returns:
            Dict with training results and model summary
        """
        if self.is_model_available() and not force_retrain:
            return {
                'success': False,
                'message': 'Model already trained. Use force_retrain=True to retrain.',
                'current_model': self.current_model.get_model_summary()
            }

        logger.info("Starting model training on full historical dataset...")

        try:
            # Load ALL historical workout data
            training_data = self._load_full_training_dataset()

            if training_data.empty:
                return {
                    'success': False,
                    'message': 'No training data available',
                    'training_data_info': {'total_workouts': 0}
                }

            # Archive current model if it exists
            if self.current_model and self.current_model.is_trained():
                self._save_model(self.current_model, archive=True)

            # Create and train new model
            new_model = self._train_kmeans_model(training_data)

            # Evaluate model performance
            self._evaluate_model_performance(new_model, training_data)

            # Save new model as active
            if self._save_model(new_model, archive=False):
                self.current_model = new_model

                return {
                    'success': True,
                    'message': 'Model trained successfully on full historical dataset',
                    'model_summary': new_model.get_model_summary(),
                    'training_data_info': new_model.training_data_info,
                    'performance_metrics': new_model.performance_metrics
                }
            else:
                return {
                    'success': False,
                    'message': 'Model training succeeded but saving failed',
                }

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {
                'success': False,
                'message': f'Model training failed: {str(e)}',
                'error': str(e)
            }

    def _load_full_training_dataset(self) -> pd.DataFrame:
        """
        Load complete historical dataset for training.

        This method loads ALL available workout data, not just recent periods.
        This is the key difference from the old approach.
        """
        try:
            query = """
            SELECT workout_date, activity_type, kcal_burned, distance_mi,
                   duration_sec, avg_pace, max_pace, steps
            FROM workout_summary
            WHERE avg_pace IS NOT NULL
              AND distance_mi IS NOT NULL
              AND duration_sec IS NOT NULL
            ORDER BY workout_date ASC
            """

            with self.db_service.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                cursor.close()

                if rows:
                    df = pd.DataFrame(rows)
                    df['duration_min'] = (df['duration_sec'] / 60).round(1)

                    # Convert workout_date to datetime
                    if df['workout_date'].dtype == 'object':
                        df['workout_date'] = pd.to_datetime(df['workout_date'])

                    logger.info(f"Loaded {len(df)} workouts for training (from {df['workout_date'].min()} to {df['workout_date'].max()})")
                    return df
                else:
                    logger.warning("No workout data found for training")
                    return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error loading training dataset: {e}")
            return pd.DataFrame()

    def _train_kmeans_model(self, training_data: pd.DataFrame) -> WorkoutClassificationModel:
        """
        Train K-means clustering model on full dataset.

        Args:
            training_data: Complete historical workout dataset

        Returns:
            Trained WorkoutClassificationModel
        """
        model = WorkoutClassificationModel()
        model.model_id = f"workout_classifier_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model.created_at = datetime.now()

        # Store training data information
        model.training_data_info = {
            'total_workouts': len(training_data),
            'date_range': {
                'start_date': training_data['workout_date'].min().strftime('%Y-%m-%d'),
                'end_date': training_data['workout_date'].max().strftime('%Y-%m-%d'),
                'span_days': (training_data['workout_date'].max() - training_data['workout_date'].min()).days
            },
            'features_used': model.feature_columns
        }

        # Prepare features for clustering
        features_df = training_data[model.feature_columns].copy()

        # Remove extreme outliers (same logic as before but on full dataset)
        pace_filter = (features_df['avg_pace'] > 0) & (features_df['avg_pace'] <= 60)
        distance_filter = (features_df['distance_mi'] > 0) & (features_df['distance_mi'] <= 50)
        duration_filter = (features_df['duration_min'] > 0) & (features_df['duration_min'] <= 1440)

        clean_features = features_df[pace_filter & distance_filter & duration_filter].dropna()

        logger.info(f"Training on {len(clean_features)} clean workouts after outlier removal")

        # Fit scaler on clean data
        model.scaler = StandardScaler()
        features_scaled = model.scaler.fit_transform(clean_features)

        # Train K-means
        model.kmeans = KMeans(n_clusters=model.n_clusters, random_state=model.random_state, n_init=10)
        cluster_labels = model.kmeans.fit_predict(features_scaled)

        # Analyze cluster centers and create activity mapping
        centers_original = model.scaler.inverse_transform(model.kmeans.cluster_centers_)
        centers_df = pd.DataFrame(centers_original, columns=model.feature_columns)
        centers_df['cluster_id'] = range(len(centers_df))

        # Sort by pace to assign activity types (fastest -> slowest)
        centers_sorted = centers_df.sort_values('avg_pace')

        for idx, (_, row) in enumerate(centers_sorted.iterrows()):
            cluster_id = int(row['cluster_id'])
            if idx == 0:  # Fastest pace cluster
                model.cluster_to_activity_map[cluster_id] = 'real_run'
            elif idx == 1:  # Medium pace cluster
                model.cluster_to_activity_map[cluster_id] = 'mixed'
            else:  # Slowest pace cluster
                model.cluster_to_activity_map[cluster_id] = 'pup_walk'

        # Calculate activity type statistics
        clean_features_with_labels = clean_features.copy()
        clean_features_with_labels['cluster'] = cluster_labels
        clean_features_with_labels['predicted_activity_type'] = [
            model.cluster_to_activity_map[cluster] for cluster in cluster_labels
        ]

        for activity_type in ['real_run', 'pup_walk', 'mixed']:
            activity_data = clean_features_with_labels[
                clean_features_with_labels['predicted_activity_type'] == activity_type
            ]

            if not activity_data.empty:
                model.activity_type_stats[activity_type] = {
                    'count': len(activity_data),
                    'avg_pace': float(activity_data['avg_pace'].mean()),
                    'avg_distance': float(activity_data['distance_mi'].mean()),
                    'avg_duration': float(activity_data['duration_min'].mean()),
                    'pace_range': [float(activity_data['avg_pace'].min()), float(activity_data['avg_pace'].max())],
                    'distance_range': [float(activity_data['distance_mi'].min()), float(activity_data['distance_mi'].max())]
                }

        model.trained_at = datetime.now()

        logger.info(f"Model training completed. Activity distribution: {dict(clean_features_with_labels['predicted_activity_type'].value_counts())}")

        return model

    def _evaluate_model_performance(self, model: WorkoutClassificationModel, training_data: pd.DataFrame):
        """
        Evaluate trained model performance using various metrics.

        Args:
            model: Trained model to evaluate
            training_data: Training dataset used
        """
        try:
            # Prepare same features used in training
            features_df = training_data[model.feature_columns].copy()
            pace_filter = (features_df['avg_pace'] > 0) & (features_df['avg_pace'] <= 60)
            distance_filter = (features_df['distance_mi'] > 0) & (features_df['distance_mi'] <= 50)
            duration_filter = (features_df['duration_min'] > 0) & (features_df['duration_min'] <= 1440)

            clean_features = features_df[pace_filter & distance_filter & duration_filter].dropna()
            features_scaled = model.scaler.transform(clean_features)

            # Calculate silhouette score
            cluster_labels = model.kmeans.predict(features_scaled)
            silhouette = silhouette_score(features_scaled, cluster_labels)

            # Calculate inertia (within-cluster sum of squares)
            inertia = model.kmeans.inertia_

            # Calculate confidence statistics
            distances = np.min(model.kmeans.transform(features_scaled), axis=1)
            max_distance = np.max(distances)
            confidences = 1.0 - (distances / max_distance) if max_distance > 0 else np.ones(len(distances))

            model.performance_metrics = {
                'silhouette_score': float(silhouette),
                'inertia': float(inertia),
                'training_samples': len(clean_features),
                'confidence_stats': {
                    'mean': float(np.mean(confidences)),
                    'median': float(np.median(confidences)),
                    'std': float(np.std(confidences)),
                    'min': float(np.min(confidences)),
                    'max': float(np.max(confidences))
                },
                'cluster_distribution': {
                    str(k): int(np.sum(cluster_labels == k)) for k in range(model.n_clusters)
                }
            }

            logger.info(f"Model evaluation completed. Silhouette score: {silhouette:.3f}")

        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            model.performance_metrics = {'error': str(e)}

    def classify_workouts(self, workouts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify workouts using the trained model.

        This method applies the pre-trained model to new workout data,
        with proper fallbacks to era-based defaults when needed.

        Args:
            workouts_df: DataFrame with workout data to classify

        Returns:
            DataFrame with added classification columns
        """
        if not self.is_model_available():
            # Fallback to era-based classification
            return self._apply_era_based_classification(workouts_df)

        result_df = workouts_df.copy()
        result_df['predicted_activity_type'] = 'unknown'
        result_df['classification_confidence'] = 0.0
        result_df['classification_method'] = 'error'

        try:
            # Prepare features
            features_df = result_df[self.current_model.feature_columns].copy()

            # Apply same outlier filtering as training
            pace_filter = (features_df['avg_pace'] > 0) & (features_df['avg_pace'] <= 60)
            distance_filter = (features_df['distance_mi'] > 0) & (features_df['distance_mi'] <= 50)
            duration_filter = (features_df['duration_min'] > 0) & (features_df['duration_min'] <= 1440)

            clean_indices = features_df[pace_filter & distance_filter & duration_filter].dropna().index

            if len(clean_indices) == 0:
                # No valid data for ML - use era-based fallback
                return self._apply_era_based_classification(result_df)

            # Apply trained scaler and model
            clean_features = features_df.loc[clean_indices]
            features_scaled = self.current_model.scaler.transform(clean_features)

            # Predict clusters
            predicted_clusters = self.current_model.kmeans.predict(features_scaled)

            # Calculate confidences
            distances = np.min(self.current_model.kmeans.transform(features_scaled), axis=1)
            max_distance = np.max(distances) if len(distances) > 0 else 1.0
            confidences = 1.0 - (distances / max_distance) if max_distance > 0 else np.ones(len(distances))

            # Apply classifications to clean indices
            for i, idx in enumerate(clean_indices):
                cluster = predicted_clusters[i]
                activity_type = self.current_model.cluster_to_activity_map.get(cluster, 'unknown')
                confidence = confidences[i]

                result_df.loc[idx, 'predicted_activity_type'] = activity_type
                result_df.loc[idx, 'classification_confidence'] = confidence
                result_df.loc[idx, 'classification_method'] = 'ml_trained'

            # Handle outliers and missing data with era-based fallback
            unclassified_mask = result_df['predicted_activity_type'] == 'unknown'
            if unclassified_mask.any():
                result_df = self._apply_era_based_fallback(result_df, unclassified_mask)

            return result_df

        except Exception as e:
            logger.error(f"ML classification failed: {e}, falling back to era-based classification")
            return self._apply_era_based_classification(workouts_df)

    def _apply_era_based_classification(self, workouts_df: pd.DataFrame) -> pd.DataFrame:
        """Apply era-based classification to all workouts."""
        result_df = workouts_df.copy()

        # Ensure workout_date is datetime
        if 'workout_date' not in result_df.columns:
            logger.warning("No workout_date column for era-based classification")
            result_df['predicted_activity_type'] = CLASSIFICATION_DEFAULTS["post_choco_era_default"]
            result_df['classification_confidence'] = 0.3
            result_df['classification_method'] = 'era_default_no_date'
            return result_df

        if result_df['workout_date'].dtype == 'object':
            result_df['workout_date'] = pd.to_datetime(result_df['workout_date'])

        choco_date = app_config.choco_effect_date

        # Apply era-based classification
        result_df['predicted_activity_type'] = result_df['workout_date'].apply(
            lambda date: CLASSIFICATION_DEFAULTS["pre_choco_era_default"] if date < choco_date
            else CLASSIFICATION_DEFAULTS["post_choco_era_default"]
        )
        result_df['classification_confidence'] = 0.5  # Medium confidence for era-based
        result_df['classification_method'] = 'era_based'

        return result_df

    def _apply_era_based_fallback(self, result_df: pd.DataFrame, unclassified_mask: pd.Series) -> pd.DataFrame:
        """Apply era-based classification to unclassified workouts."""
        if 'workout_date' not in result_df.columns:
            result_df.loc[unclassified_mask, 'predicted_activity_type'] = CLASSIFICATION_DEFAULTS["post_choco_era_default"]
            result_df.loc[unclassified_mask, 'classification_confidence'] = 0.3
            result_df.loc[unclassified_mask, 'classification_method'] = 'era_fallback_no_date'
            return result_df

        choco_date = app_config.choco_effect_date

        # Apply era-based classification to unclassified rows
        unclassified_indices = result_df[unclassified_mask].index

        for idx in unclassified_indices:
            workout_date = pd.to_datetime(result_df.loc[idx, 'workout_date'])
            if workout_date < choco_date:
                result_df.loc[idx, 'predicted_activity_type'] = CLASSIFICATION_DEFAULTS["pre_choco_era_default"]
            else:
                result_df.loc[idx, 'predicted_activity_type'] = CLASSIFICATION_DEFAULTS["post_choco_era_default"]

            result_df.loc[idx, 'classification_confidence'] = 0.4  # Lower confidence for fallback
            result_df.loc[idx, 'classification_method'] = 'era_fallback'

        return result_df

    def get_model_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the current model and its performance."""
        if not self.is_model_available():
            return {
                'model_available': False,
                'message': 'No trained model available'
            }

        model_summary = self.current_model.get_model_summary()

        return {
            'model_available': True,
            'model_summary': model_summary,
            'activity_type_stats': self.current_model.activity_type_stats,
            'performance_metrics': self.current_model.performance_metrics,
            'training_data_info': self.current_model.training_data_info,
            'model_files_exist': self._check_model_files_exist()
        }

    def get_archived_models(self) -> List[Dict[str, Any]]:
        """Get list of archived models with their metadata."""
        archive_dir = self.models_dir / "archive"
        archived_models = []

        if not archive_dir.exists():
            return archived_models

        try:
            # Find all archived model metadata files
            for metadata_file in archive_dir.glob("model_*.json"):
                try:
                    with open(metadata_file, 'r') as f:
                        model_data = json.load(f)

                    # Create basic summary
                    archived_models.append({
                        'model_id': model_data.get('model_id'),
                        'version': model_data.get('version', '1.0.0'),
                        'trained_at': model_data.get('trained_at'),
                        'training_workouts': model_data.get('training_data_info', {}).get('total_workouts', 0),
                        'silhouette_score': model_data.get('performance_metrics', {}).get('silhouette_score', 0),
                        'clusters': model_data.get('n_clusters', 3),
                        'metadata_file': str(metadata_file)
                    })

                except Exception as e:
                    logger.warning(f"Could not load archived model {metadata_file}: {e}")
                    continue

            # Sort by training date (newest first)
            archived_models.sort(key=lambda x: x['trained_at'] if x['trained_at'] else '', reverse=True)

        except Exception as e:
            logger.error(f"Error reading archived models: {e}")

        return archived_models

    def get_model_comparison(self, current_model_id: str, archived_model_ids: List[str]) -> Dict[str, Any]:
        """Compare current model with archived models."""
        try:
            comparison = {
                'current_model': self.get_model_stats() if self.is_model_available() else None,
                'archived_models': [],
                'comparison_metrics': []
            }

            archived_models = self.get_archived_models()

            for archived in archived_models:
                if archived['model_id'] in archived_model_ids:
                    comparison['archived_models'].append(archived)

            # Generate comparison metrics if we have models to compare
            if comparison['current_model'] and comparison['archived_models']:
                current_perf = comparison['current_model']['performance_metrics']

                for archived in comparison['archived_models']:
                    # Load full archived model data
                    metadata_file = archived['metadata_file']
                    with open(metadata_file, 'r') as f:
                        archived_data = json.load(f)

                    archived_perf = archived_data.get('performance_metrics', {})

                    if 'silhouette_score' in current_perf and 'silhouette_score' in archived_perf:
                        perf_improvement = current_perf['silhouette_score'] - archived_perf['silhouette_score']

                        comparison['comparison_metrics'].append({
                            'archived_model_id': archived['model_id'],
                            'silhouette_improvement': perf_improvement,
                            'training_data_change': (
                                comparison['current_model']['training_data_info']['total_workouts'] -
                                archived_data.get('training_data_info', {}).get('total_workouts', 0)
                            )
                        })

            return comparison

        except Exception as e:
            logger.error(f"Error generating model comparison: {e}")
            return {'error': str(e)}

    def _check_model_files_exist(self) -> Dict[str, bool]:
        """Check if model files exist on disk."""
        active_model_path = self.models_dir / "active" / "current_model"
        return {
            'metadata_file': active_model_path.with_suffix('.json').exists(),
            'sklearn_file': active_model_path.with_suffix('.pkl').exists(),
            'models_directory': self.models_dir.exists()
        }


# Global model manager instance for easy access
model_manager = ModelManager()