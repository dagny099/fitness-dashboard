"""
Enhanced Model Manager with Audit Integration

This is an enhanced version of ModelManager that integrates with the audit system
for complete model versioning and classification tracking.

Key Enhancements:
- Automatic model registration in ml_model_registry
- Classification audit logging for all predictions
- Model lineage tracking (parent-child relationships)
- Performance comparison across model versions
- Integration with user feedback system

Usage:
    from ml.model_manager_v2 import EnhancedModelManager

    manager = EnhancedModelManager()
    manager.train_and_register_model()
    manager.classify_and_log_workouts(df)
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
from services.audit_service import AuditService
from ml.model_manager import WorkoutClassificationModel
import logging

logger = logging.getLogger(__name__)


class EnhancedModelManager:
    """
    Enhanced ML model manager with complete audit trail integration.

    This class extends the basic ModelManager with:
    - Automatic model registration
    - Classification audit logging
    - Model version management
    - Performance tracking
    """

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        audit_service: Optional[AuditService] = None,
        models_dir: str = "models"
    ):
        """
        Initialize enhanced model manager.

        Args:
            db_service: Database service for data access
            audit_service: Audit service for logging
            models_dir: Directory for model storage
        """
        self.db_service = db_service or DatabaseService()
        self.audit_service = audit_service or AuditService(self.db_service)

        # Create models directory structure
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        (self.models_dir / "active").mkdir(exist_ok=True)
        (self.models_dir / "archive").mkdir(exist_ok=True)

        self.current_model: Optional[WorkoutClassificationModel] = None
        self.current_model_db_info: Optional[Dict] = None

        # Try to load existing active model
        self._load_active_model()

    def _load_active_model(self) -> bool:
        """
        Load the currently active model from database registry and disk.

        Returns:
            bool: True if model loaded successfully
        """
        # First, check database for active model
        active_model_db = self.audit_service.get_active_model()

        if not active_model_db:
            logger.info("No active model in registry. Training will be required.")
            return False

        model_id = active_model_db['model_id']
        logger.info(f"Found active model in registry: {model_id}")

        # Try to load model files from disk
        model_file_path = active_model_db.get('model_file_path')
        metadata_file_path = active_model_db.get('metadata_file_path')

        if not (model_file_path and metadata_file_path):
            # Fall back to default paths
            active_model_path = self.models_dir / "active" / "current_model"
            metadata_file_path = str(active_model_path.with_suffix('.json'))
            model_file_path = str(active_model_path.with_suffix('.pkl'))

        try:
            # Load metadata
            with open(metadata_file_path, 'r') as f:
                metadata = json.load(f)

            # Load sklearn objects
            with open(model_file_path, 'rb') as f:
                sklearn_objects = pickle.load(f)

            # Reconstruct model
            self.current_model = WorkoutClassificationModel()
            self.current_model.from_dict(metadata)
            self.current_model.kmeans = sklearn_objects['kmeans']
            self.current_model.scaler = sklearn_objects['scaler']

            # Store DB info for reference
            self.current_model_db_info = active_model_db

            logger.info(f"Loaded active model: {model_id} (version {active_model_db['model_version']})")
            return True

        except Exception as e:
            logger.error(f"Failed to load model files for {model_id}: {e}")
            return False

    def train_and_register_model(
        self,
        force_retrain: bool = False,
        parent_model_id: Optional[str] = None,
        training_notes: Optional[str] = None,
        auto_activate: bool = True
    ) -> Dict[str, Any]:
        """
        Train a new model and register it in the database.

        Args:
            force_retrain: Retrain even if active model exists
            parent_model_id: Parent model ID for lineage tracking
            training_notes: Notes about this training run
            auto_activate: Automatically activate model if training succeeds

        Returns:
            Dict with training and registration results
        """
        if self.current_model and not force_retrain:
            return {
                'success': False,
                'message': 'Model already trained. Use force_retrain=True to retrain.'
            }

        logger.info("Starting model training with audit integration...")

        try:
            # Load full training dataset
            training_data = self._load_full_training_dataset()

            if training_data.empty:
                return {
                    'success': False,
                    'message': 'No training data available'
                }

            # Archive current model if it exists
            if self.current_model and hasattr(self.current_model, 'model_id'):
                old_model_id = self.current_model.model_id
                parent_model_id = parent_model_id or old_model_id
                self._save_model(self.current_model, archive=True)

            # Train new model
            training_start = datetime.now()
            new_model = self._train_kmeans_model(training_data)
            self._evaluate_model_performance(new_model, training_data)
            training_end = datetime.now()
            training_duration = (training_end - training_start).total_seconds()

            # Save model to disk
            if not self._save_model(new_model, archive=False):
                return {
                    'success': False,
                    'message': 'Model training succeeded but file save failed'
                }

            # Register model in database
            registration_success = self._register_model_in_db(
                model=new_model,
                training_duration=training_duration,
                parent_model_id=parent_model_id,
                training_notes=training_notes
            )

            if not registration_success:
                logger.warning("Model trained but registration in DB failed")

            # Set as current model
            self.current_model = new_model

            # Auto-activate if requested
            if auto_activate and registration_success:
                activation_success = self.audit_service.activate_model(new_model.model_id)
                if activation_success:
                    # Reload model DB info
                    self.current_model_db_info = self.audit_service.get_model_by_id(
                        new_model.model_id
                    )

            result = {
                'success': True,
                'message': 'Model trained and registered successfully',
                'model_id': new_model.model_id,
                'model_version': new_model.version,
                'training_duration_sec': training_duration,
                'registered_in_db': registration_success,
                'activated': auto_activate and registration_success,
                'model_summary': new_model.get_model_summary(),
                'performance_metrics': new_model.performance_metrics
            }

            logger.info(f"Model training completed: {new_model.model_id}")
            return result

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {
                'success': False,
                'message': f'Training failed: {str(e)}',
                'error': str(e)
            }

    def _load_full_training_dataset(self) -> pd.DataFrame:
        """Load complete historical dataset for training."""
        try:
            query = """
            SELECT workout_id, workout_date, activity_type, kcal_burned, distance_mi,
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

                    if df['workout_date'].dtype == 'object':
                        df['workout_date'] = pd.to_datetime(df['workout_date'])

                    logger.info(f"Loaded {len(df)} workouts for training")
                    return df
                else:
                    logger.warning("No workout data found for training")
                    return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error loading training dataset: {e}")
            return pd.DataFrame()

    def _train_kmeans_model(self, training_data: pd.DataFrame) -> WorkoutClassificationModel:
        """Train K-means clustering model (same as base ModelManager)."""
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

        # Prepare features
        features_df = training_data[model.feature_columns].copy()

        # Filter outliers
        pace_filter = (features_df['avg_pace'] > 0) & (features_df['avg_pace'] <= 60)
        distance_filter = (features_df['distance_mi'] > 0) & (features_df['distance_mi'] <= 50)
        duration_filter = (features_df['duration_min'] > 0) & (features_df['duration_min'] <= 1440)

        clean_features = features_df[pace_filter & distance_filter & duration_filter].dropna()

        logger.info(f"Training on {len(clean_features)} clean workouts")

        # Fit scaler and K-means
        model.scaler = StandardScaler()
        features_scaled = model.scaler.fit_transform(clean_features)

        model.kmeans = KMeans(n_clusters=model.n_clusters, random_state=model.random_state, n_init=10)
        cluster_labels = model.kmeans.fit_predict(features_scaled)

        # Create activity mapping by pace
        centers_original = model.scaler.inverse_transform(model.kmeans.cluster_centers_)
        centers_df = pd.DataFrame(centers_original, columns=model.feature_columns)
        centers_df['cluster_id'] = range(len(centers_df))
        centers_sorted = centers_df.sort_values('avg_pace')

        for idx, (_, row) in enumerate(centers_sorted.iterrows()):
            cluster_id = int(row['cluster_id'])
            if idx == 0:
                model.cluster_to_activity_map[cluster_id] = 'real_run'
            elif idx == 1:
                model.cluster_to_activity_map[cluster_id] = 'mixed'
            else:
                model.cluster_to_activity_map[cluster_id] = 'pup_walk'

        # Calculate activity type stats
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

        logger.info(f"Model training completed")
        return model

    def _evaluate_model_performance(self, model: WorkoutClassificationModel, training_data: pd.DataFrame):
        """Evaluate model performance (same as base ModelManager)."""
        try:
            features_df = training_data[model.feature_columns].copy()
            pace_filter = (features_df['avg_pace'] > 0) & (features_df['avg_pace'] <= 60)
            distance_filter = (features_df['distance_mi'] > 0) & (features_df['distance_mi'] <= 50)
            duration_filter = (features_df['duration_min'] > 0) & (features_df['duration_min'] <= 1440)

            clean_features = features_df[pace_filter & distance_filter & duration_filter].dropna()
            features_scaled = model.scaler.transform(clean_features)

            cluster_labels = model.kmeans.predict(features_scaled)
            silhouette = silhouette_score(features_scaled, cluster_labels)
            inertia = model.kmeans.inertia_

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

            logger.info(f"Model evaluation completed. Silhouette: {silhouette:.3f}")

        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            model.performance_metrics = {'error': str(e)}

    def _save_model(self, model: WorkoutClassificationModel, archive: bool = False) -> bool:
        """Save model to disk."""
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

    def _register_model_in_db(
        self,
        model: WorkoutClassificationModel,
        training_duration: float,
        parent_model_id: Optional[str] = None,
        training_notes: Optional[str] = None
    ) -> bool:
        """Register model in database registry."""
        try:
            training_info = model.training_data_info

            # Parse dates from training info
            start_date = datetime.strptime(training_info['date_range']['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(training_info['date_range']['end_date'], '%Y-%m-%d')

            # Build model file paths
            model_file_path = str(self.models_dir / "active" / "current_model.pkl")
            metadata_file_path = str(self.models_dir / "active" / "current_model.json")

            success = self.audit_service.register_model(
                model_id=model.model_id,
                model_name="Workout Classifier",
                model_version=model.version,
                cluster_to_activity_map={str(k): v for k, v in model.cluster_to_activity_map.items()},
                training_workouts_count=training_info['total_workouts'],
                training_date_start=start_date,
                training_date_end=end_date,
                training_features=model.feature_columns,
                silhouette_score=model.performance_metrics.get('silhouette_score', 0),
                inertia=model.performance_metrics.get('inertia', 0),
                cluster_distribution=model.performance_metrics.get('cluster_distribution', {}),
                confidence_stats=model.performance_metrics.get('confidence_stats', {}),
                activity_type_stats=model.activity_type_stats,
                n_clusters=model.n_clusters,
                algorithm_type='kmeans',
                hyperparameters={
                    'n_init': 10,
                    'random_state': model.random_state,
                    'confidence_threshold': model.confidence_threshold
                },
                model_file_path=model_file_path,
                metadata_file_path=metadata_file_path,
                parent_model_id=parent_model_id,
                training_notes=training_notes
            )

            return success

        except Exception as e:
            logger.error(f"Failed to register model in database: {e}")
            return False

    def classify_and_log_workouts(
        self,
        workouts_df: pd.DataFrame,
        log_to_audit: bool = True,
        persist_classifications: bool = True
    ) -> pd.DataFrame:
        """
        Classify workouts and optionally log to audit history.

        Args:
            workouts_df: DataFrame with workout data
            log_to_audit: Log classifications to audit history
            persist_classifications: Persist to workout_ml_classifications table

        Returns:
            DataFrame with classification columns added
        """
        if not self.current_model:
            logger.error("No model available for classification")
            return workouts_df

        result_df = workouts_df.copy()
        result_df['predicted_activity_type'] = 'unknown'
        result_df['classification_confidence'] = 0.0
        result_df['classification_method'] = 'error'

        try:
            # Prepare features
            features_df = result_df[self.current_model.feature_columns].copy()

            # Apply outlier filtering
            pace_filter = (features_df['avg_pace'] > 0) & (features_df['avg_pace'] <= 60)
            distance_filter = (features_df['distance_mi'] > 0) & (features_df['distance_mi'] <= 50)
            duration_filter = (features_df['duration_min'] > 0) & (features_df['duration_min'] <= 1440)

            clean_indices = features_df[pace_filter & distance_filter & duration_filter].dropna().index

            if len(clean_indices) == 0:
                logger.warning("No valid data for ML classification")
                return result_df

            # Apply model
            clean_features = features_df.loc[clean_indices]
            features_scaled = self.current_model.scaler.transform(clean_features)

            predicted_clusters = self.current_model.kmeans.predict(features_scaled)

            # Calculate confidences
            distances = np.min(self.current_model.kmeans.transform(features_scaled), axis=1)
            max_distance = np.max(distances) if len(distances) > 0 else 1.0
            confidences = 1.0 - (distances / max_distance) if max_distance > 0 else np.ones(len(distances))

            # Prepare batch audit log
            audit_records = []

            # Apply classifications
            for i, idx in enumerate(clean_indices):
                cluster = predicted_clusters[i]
                activity_type = self.current_model.cluster_to_activity_map.get(str(cluster), 'unknown')
                confidence = confidences[i]

                result_df.loc[idx, 'predicted_activity_type'] = activity_type
                result_df.loc[idx, 'classification_confidence'] = confidence
                result_df.loc[idx, 'classification_method'] = 'ml_trained'

                # Prepare audit record
                if log_to_audit and 'workout_id' in result_df.columns:
                    workout_id = result_df.loc[idx, 'workout_id']

                    audit_records.append({
                        'workout_id': workout_id,
                        'previous_classification': None,  # Could query current if needed
                        'new_classification': activity_type,
                        'source': 'ml_prediction',
                        'confidence': float(confidence),
                        'method': 'ml_trained',
                        'model_id': self.current_model.model_id,
                        'model_version': self.current_model.version,
                        'features_used': {
                            feature: float(result_df.loc[idx, feature])
                            for feature in self.current_model.feature_columns
                            if feature in result_df.columns
                        }
                    })

                    # Persist classification if requested
                    if persist_classifications:
                        self.audit_service.persist_classification(
                            workout_id=workout_id,
                            classification=activity_type,
                            source='ml_prediction',
                            confidence=float(confidence),
                            method='ml_trained',
                            model_id=self.current_model.model_id,
                            model_version=self.current_model.version,
                            features_snapshot={
                                feature: float(result_df.loc[idx, feature])
                                for feature in self.current_model.feature_columns
                                if feature in result_df.columns
                            }
                        )

            # Batch log to audit history
            if audit_records:
                success_count, fail_count = self.audit_service.log_batch_classifications(
                    audit_records,
                    model_id=self.current_model.model_id,
                    model_version=self.current_model.version
                )
                logger.info(f"Audit logging: {success_count} success, {fail_count} failed")

            return result_df

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return result_df


# Example usage and testing
if __name__ == "__main__":
    # Example: Train and classify with audit trail
    manager = EnhancedModelManager()

    # Train new model with versioning
    result = manager.train_and_register_model(
        force_retrain=True,
        training_notes="Initial model with audit integration",
        auto_activate=True
    )

    print(f"Training result: {result['success']}")
    print(f"Model ID: {result.get('model_id')}")

    # Classify workouts with audit logging
    # df = load_workout_data()  # Your data loading function
    # classified_df = manager.classify_and_log_workouts(df, log_to_audit=True)
