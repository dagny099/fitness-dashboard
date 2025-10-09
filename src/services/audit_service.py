"""
Audit Service for Classification History and Model Versioning

This service provides centralized logging and tracking for:
- Workout classification changes (audit history)
- ML model version management
- User feedback collection
- Classification persistence

Design Philosophy:
- Separation of concerns: Audit logic separate from business logic
- Performance: Async-friendly design for batch operations
- Traceability: Complete audit trail for compliance
- Analytics: Rich data for model improvement
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

from services.database_service import DatabaseService
from config.database import DatabaseConfig

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit history and model versioning operations."""

    def __init__(self, db_service: Optional[DatabaseService] = None):
        """Initialize audit service with database connection."""
        self.db_service = db_service or DatabaseService()

    # ========================================================================
    # CLASSIFICATION AUDIT HISTORY
    # ========================================================================

    def log_classification_change(
        self,
        workout_id: str,
        previous_classification: Optional[str],
        new_classification: str,
        source: str,
        confidence: Optional[float] = None,
        method: Optional[str] = None,
        model_id: Optional[str] = None,
        model_version: Optional[str] = None,
        changed_by: str = 'system',
        reason: Optional[str] = None,
        features_used: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Log a classification change to audit history.

        Args:
            workout_id: Workout identifier
            previous_classification: Previous classification (None if first classification)
            new_classification: New classification value
            source: Source of classification ('csv_import', 'ml_prediction', etc.)
            confidence: Classification confidence score (0-1)
            method: Method used ('ml_trained', 'era_based', etc.)
            model_id: ML model identifier that made prediction
            model_version: Model version string
            changed_by: User or system that made the change
            reason: Optional explanation for the change
            features_used: Features used for classification
            metadata: Additional context

        Returns:
            bool: True if logged successfully
        """
        query = """
            INSERT INTO workout_classification_history
            (workout_id, previous_classification, new_classification,
             classification_source, classification_confidence, classification_method,
             model_id, model_version, changed_by, reason, features_used, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            # Convert dictionaries to JSON strings
            features_json = json.dumps(features_used) if features_used else None
            metadata_json = json.dumps(metadata) if metadata else None

            affected_rows = self.db_service.execute_update(
                query,
                (
                    workout_id,
                    previous_classification,
                    new_classification,
                    source,
                    confidence,
                    method,
                    model_id,
                    model_version,
                    changed_by,
                    reason,
                    features_json,
                    metadata_json
                )
            )

            if affected_rows > 0:
                logger.info(
                    f"Logged classification change for {workout_id}: "
                    f"{previous_classification} → {new_classification} "
                    f"(source: {source}, confidence: {confidence:.2f if confidence else 'N/A'})"
                )
                return True
            else:
                logger.warning(f"Classification change not logged for {workout_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to log classification change for {workout_id}: {e}")
            return False

    def log_batch_classifications(
        self,
        classifications: List[Dict[str, Any]],
        model_id: Optional[str] = None,
        model_version: Optional[str] = None
    ) -> Tuple[int, int]:
        """
        Log multiple classification changes in batch (more efficient).

        Args:
            classifications: List of classification dicts with keys:
                - workout_id (required)
                - previous_classification
                - new_classification (required)
                - source (required)
                - confidence
                - method
                - features_used
                - metadata
            model_id: Model ID to apply to all (can be overridden per item)
            model_version: Model version to apply to all

        Returns:
            Tuple[int, int]: (successful_count, failed_count)
        """
        if not classifications:
            logger.warning("log_batch_classifications called with empty list")
            return (0, 0)

        success_count = 0
        failed_count = 0

        query = """
            INSERT INTO workout_classification_history
            (workout_id, previous_classification, new_classification,
             classification_source, classification_confidence, classification_method,
             model_id, model_version, changed_by, reason, features_used, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            with self.db_service.get_connection() as connection:
                with connection.cursor() as cursor:
                    for item in classifications:
                        try:
                            # Extract values with defaults
                            workout_id = item['workout_id']
                            prev_class = item.get('previous_classification')
                            new_class = item['new_classification']
                            source = item['source']
                            confidence = item.get('confidence')
                            method = item.get('method')
                            item_model_id = item.get('model_id', model_id)
                            item_model_version = item.get('model_version', model_version)
                            changed_by = item.get('changed_by', 'system')
                            reason = item.get('reason')
                            features = item.get('features_used')
                            meta = item.get('metadata')

                            # Convert dicts to JSON
                            features_json = json.dumps(features) if features else None
                            meta_json = json.dumps(meta) if meta else None

                            cursor.execute(
                                query,
                                (
                                    workout_id, prev_class, new_class, source,
                                    confidence, method, item_model_id, item_model_version,
                                    changed_by, reason, features_json, meta_json
                                )
                            )
                            success_count += 1

                        except KeyError as e:
                            logger.error(f"Missing required field in classification item: {e}")
                            failed_count += 1
                        except Exception as e:
                            logger.error(f"Failed to log classification for {item.get('workout_id', 'unknown')}: {e}")
                            failed_count += 1

                    # Commit all changes
                    connection.commit()

            logger.info(f"Batch classification logging completed: {success_count} success, {failed_count} failed")
            return (success_count, failed_count)

        except Exception as e:
            logger.error(f"Batch classification logging failed: {e}")
            return (success_count, failed_count)

    def get_classification_history(
        self,
        workout_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve complete classification history for a workout.

        Args:
            workout_id: Workout identifier
            limit: Optional limit on number of history entries

        Returns:
            List of classification history records (most recent first)
        """
        query = """
            SELECT
                history_id,
                previous_classification,
                new_classification,
                classification_source,
                classification_confidence,
                classification_method,
                model_id,
                model_version,
                changed_by,
                changed_at,
                reason,
                features_used,
                metadata
            FROM workout_classification_history
            WHERE workout_id = %s
            ORDER BY changed_at DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        try:
            results = self.db_service.execute_query(query, (workout_id,))

            # Parse JSON fields
            for result in results:
                if result.get('features_used'):
                    result['features_used'] = json.loads(result['features_used'])
                if result.get('metadata'):
                    result['metadata'] = json.loads(result['metadata'])

            return results

        except Exception as e:
            logger.error(f"Failed to retrieve classification history for {workout_id}: {e}")
            return []

    def get_classification_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get aggregate statistics on classification changes.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            source_filter: Optional filter by classification source

        Returns:
            Dict with statistics on classification changes
        """
        base_query = """
            SELECT
                classification_source,
                COUNT(*) as total_changes,
                AVG(classification_confidence) as avg_confidence,
                COUNT(DISTINCT workout_id) as unique_workouts,
                COUNT(DISTINCT model_id) as unique_models
            FROM workout_classification_history
            WHERE 1=1
        """

        params = []

        if start_date:
            base_query += " AND changed_at >= %s"
            params.append(start_date)

        if end_date:
            base_query += " AND changed_at <= %s"
            params.append(end_date)

        if source_filter:
            base_query += " AND classification_source = %s"
            params.append(source_filter)

        base_query += " GROUP BY classification_source"

        try:
            results = self.db_service.execute_query(base_query, tuple(params))

            # Build stats summary
            stats = {
                'by_source': results,
                'total_changes': sum(r['total_changes'] for r in results),
                'unique_workouts': max((r['unique_workouts'] for r in results), default=0),
                'date_range': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                }
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get classification stats: {e}")
            return {'error': str(e)}

    # ========================================================================
    # ML MODEL REGISTRY
    # ========================================================================

    def register_model(
        self,
        model_id: str,
        model_name: str,
        model_version: str,
        cluster_to_activity_map: Dict,
        training_workouts_count: int,
        training_date_start: datetime,
        training_date_end: datetime,
        training_features: List[str],
        silhouette_score: float,
        inertia: float,
        cluster_distribution: Dict,
        confidence_stats: Dict,
        activity_type_stats: Dict,
        n_clusters: int = 3,
        algorithm_type: str = 'kmeans',
        hyperparameters: Optional[Dict] = None,
        model_file_path: Optional[str] = None,
        metadata_file_path: Optional[str] = None,
        parent_model_id: Optional[str] = None,
        training_notes: Optional[str] = None,
        created_by: str = 'system'
    ) -> bool:
        """
        Register a new ML model in the registry.

        Args:
            model_id: Unique model identifier
            model_name: Human-readable model name
            model_version: Semantic version (e.g., "1.0.0")
            cluster_to_activity_map: Dict mapping cluster IDs to activity types
            training_workouts_count: Number of workouts used for training
            training_date_start: Start date of training data
            training_date_end: End date of training data
            training_features: List of features used
            silhouette_score: Model silhouette score
            inertia: Model inertia (within-cluster sum of squares)
            cluster_distribution: Dict with cluster sizes
            confidence_stats: Dict with confidence statistics
            activity_type_stats: Dict with activity type statistics
            n_clusters: Number of clusters
            algorithm_type: Algorithm used (default: 'kmeans')
            hyperparameters: Model hyperparameters
            model_file_path: Path to saved model file
            metadata_file_path: Path to metadata file
            parent_model_id: Parent model ID (for lineage tracking)
            training_notes: Notes about training process
            created_by: Who created/trained the model

        Returns:
            bool: True if registered successfully
        """
        query = """
            INSERT INTO ml_model_registry
            (model_id, model_name, model_version, status,
             trained_at, training_workouts_count, training_date_start, training_date_end,
             training_features, silhouette_score, inertia, cluster_distribution,
             confidence_stats, n_clusters, algorithm_type, hyperparameters,
             cluster_to_activity_map, activity_type_stats, model_file_path,
             metadata_file_path, parent_model_id, created_by, training_notes)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            # Convert complex types to JSON
            training_features_json = json.dumps(training_features)
            cluster_dist_json = json.dumps(cluster_distribution)
            confidence_json = json.dumps(confidence_stats)
            hyperparams_json = json.dumps(hyperparameters) if hyperparameters else None
            cluster_map_json = json.dumps(cluster_to_activity_map)
            activity_stats_json = json.dumps(activity_type_stats)

            affected_rows = self.db_service.execute_update(
                query,
                (
                    model_id, model_name, model_version, 'training',
                    datetime.now(), training_workouts_count, training_date_start,
                    training_date_end, training_features_json, silhouette_score,
                    inertia, cluster_dist_json, confidence_json, n_clusters,
                    algorithm_type, hyperparams_json, cluster_map_json,
                    activity_stats_json, model_file_path, metadata_file_path,
                    parent_model_id, created_by, training_notes
                )
            )

            if affected_rows > 0:
                logger.info(f"Registered model {model_id} (version {model_version}) in registry")
                return True
            else:
                logger.warning(f"Model {model_id} not registered")
                return False

        except Exception as e:
            logger.error(f"Failed to register model {model_id}: {e}")
            return False

    def activate_model(self, model_id: str) -> bool:
        """
        Activate a model (set as production-ready).

        This will:
        1. Set the model status to 'active'
        2. Set is_production = TRUE
        3. Deactivate any other production models
        4. Record activation timestamp

        Args:
            model_id: Model identifier to activate

        Returns:
            bool: True if activated successfully
        """
        try:
            with self.db_service.get_connection() as connection:
                with connection.cursor() as cursor:
                    # Deactivate current production model
                    cursor.execute(
                        """
                        UPDATE ml_model_registry
                        SET is_production = FALSE, status = 'archived'
                        WHERE is_production = TRUE AND model_id != %s
                        """,
                        (model_id,)
                    )

                    # Activate new model
                    cursor.execute(
                        """
                        UPDATE ml_model_registry
                        SET status = 'active', is_production = TRUE, activated_at = %s
                        WHERE model_id = %s
                        """,
                        (datetime.now(), model_id)
                    )

                    affected = cursor.rowcount
                    connection.commit()

                    if affected > 0:
                        logger.info(f"Activated model {model_id} as production model")
                        return True
                    else:
                        logger.warning(f"Model {model_id} not found for activation")
                        return False

        except Exception as e:
            logger.error(f"Failed to activate model {model_id}: {e}")
            return False

    def get_active_model(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently active production model.

        Returns:
            Dict with model information, or None if no active model
        """
        query = """
            SELECT * FROM ml_model_registry
            WHERE is_production = TRUE AND status = 'active'
            LIMIT 1
        """

        try:
            results = self.db_service.execute_query(query)

            if results:
                model = results[0]
                # Parse JSON fields
                self._parse_model_json_fields(model)
                return model
            else:
                logger.info("No active production model found")
                return None

        except Exception as e:
            logger.error(f"Failed to get active model: {e}")
            return None

    def get_model_by_id(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model information by ID."""
        query = "SELECT * FROM ml_model_registry WHERE model_id = %s"

        try:
            results = self.db_service.execute_query(query, (model_id,))

            if results:
                model = results[0]
                self._parse_model_json_fields(model)
                return model
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get model {model_id}: {e}")
            return None

    def list_models(
        self,
        status_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List all models in registry.

        Args:
            status_filter: Optional status filter ('active', 'archived', etc.)
            limit: Maximum number of models to return

        Returns:
            List of model records
        """
        query = "SELECT * FROM ml_model_registry"

        if status_filter:
            query += " WHERE status = %s"
            params = (status_filter,)
        else:
            params = ()

        query += " ORDER BY trained_at DESC LIMIT %s"
        params = params + (limit,)

        try:
            results = self.db_service.execute_query(query, params)

            for model in results:
                self._parse_model_json_fields(model)

            return results

        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def _parse_model_json_fields(self, model: Dict[str, Any]) -> None:
        """Parse JSON fields in model record (in-place)."""
        json_fields = [
            'training_features', 'cluster_distribution', 'confidence_stats',
            'hyperparameters', 'cluster_to_activity_map', 'activity_type_stats'
        ]

        for field in json_fields:
            if model.get(field):
                try:
                    model[field] = json.loads(model[field])
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"Failed to parse JSON field {field} in model {model.get('model_id')}")
                    model[field] = None

    # ========================================================================
    # USER FEEDBACK COLLECTION
    # ========================================================================

    def save_user_feedback(
        self,
        workout_id: str,
        ai_classification: str,
        ai_confidence: float,
        feedback_type: str,
        user_classification: Optional[str] = None,
        user_certainty: Optional[int] = None,
        comments: Optional[str] = None,
        model_id: Optional[str] = None,
        classification_method: Optional[str] = None,
        user_id: str = 'anonymous',
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Save user feedback on classification.

        Args:
            workout_id: Workout identifier
            ai_classification: AI's classification
            ai_confidence: AI's confidence score
            feedback_type: Type of feedback ('accept', 'reject', 'correct', 'uncertain')
            user_classification: User's classification (if correcting)
            user_certainty: User's certainty level (1-5)
            comments: User comments
            model_id: Model that made the classification
            classification_method: Method used
            user_id: User identifier
            ip_address: User's IP address

        Returns:
            bool: True if saved successfully
        """
        query = """
            INSERT INTO user_classification_feedback
            (workout_id, ai_classification, ai_confidence, user_classification,
             feedback_type, user_certainty, comments, model_id,
             classification_method, user_id, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            affected_rows = self.db_service.execute_update(
                query,
                (
                    workout_id, ai_classification, ai_confidence,
                    user_classification, feedback_type, user_certainty,
                    comments, model_id, classification_method,
                    user_id, ip_address
                )
            )

            if affected_rows > 0:
                logger.info(f"Saved user feedback for {workout_id}: {feedback_type}")
                return True
            else:
                logger.warning(f"User feedback not saved for {workout_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to save user feedback for {workout_id}: {e}")
            return False

    def get_unprocessed_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get unprocessed user feedback for model improvement.

        Args:
            limit: Maximum number of feedback items to return

        Returns:
            List of feedback records
        """
        query = """
            SELECT * FROM user_classification_feedback
            WHERE processed = FALSE
            ORDER BY submitted_at ASC
            LIMIT %s
        """

        try:
            return self.db_service.execute_query(query, (limit,))
        except Exception as e:
            logger.error(f"Failed to get unprocessed feedback: {e}")
            return []

    # ========================================================================
    # CLASSIFICATION PERSISTENCE
    # ========================================================================

    def persist_classification(
        self,
        workout_id: str,
        classification: str,
        source: str,
        confidence: float,
        method: str,
        model_id: Optional[str] = None,
        model_version: Optional[str] = None,
        is_user_override: bool = False,
        original_ml_classification: Optional[str] = None,
        override_reason: Optional[str] = None,
        features_snapshot: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Persist classification to workout_ml_classifications table.

        This provides fast lookup of current classifications without
        querying the full audit history.

        Args:
            workout_id: Workout identifier
            classification: Classification value
            source: Classification source
            confidence: Confidence score
            method: Classification method
            model_id: Model identifier
            model_version: Model version
            is_user_override: Whether this is a user override
            original_ml_classification: Original ML classification (if override)
            override_reason: Reason for override
            features_snapshot: Features used
            metadata: Additional metadata

        Returns:
            bool: True if persisted successfully
        """
        query = """
            INSERT INTO workout_ml_classifications
            (workout_id, current_classification, classification_source,
             classification_confidence, classification_method, model_id,
             model_version, is_user_override, original_ml_classification,
             override_reason, features_snapshot, metadata, classification_change_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                current_classification = VALUES(current_classification),
                classification_source = VALUES(classification_source),
                classification_confidence = VALUES(classification_confidence),
                classification_method = VALUES(classification_method),
                model_id = VALUES(model_id),
                model_version = VALUES(model_version),
                is_user_override = VALUES(is_user_override),
                original_ml_classification = VALUES(original_ml_classification),
                override_reason = VALUES(override_reason),
                features_snapshot = VALUES(features_snapshot),
                metadata = VALUES(metadata),
                classification_change_count = classification_change_count + 1
        """

        try:
            features_json = json.dumps(features_snapshot) if features_snapshot else None
            metadata_json = json.dumps(metadata) if metadata else None

            affected_rows = self.db_service.execute_update(
                query,
                (
                    workout_id, classification, source, confidence, method,
                    model_id, model_version, is_user_override,
                    original_ml_classification, override_reason,
                    features_json, metadata_json
                )
            )

            if affected_rows > 0:
                logger.debug(f"Persisted classification for {workout_id}: {classification}")
                return True
            else:
                logger.warning(f"Classification not persisted for {workout_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to persist classification for {workout_id}: {e}")
            return False

    def get_persisted_classifications(
        self,
        workout_ids: Optional[List[str]] = None,
        model_id: Optional[str] = None,
        is_override_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get persisted classifications.

        Args:
            workout_ids: Optional list of workout IDs to filter
            model_id: Optional model ID filter
            is_override_only: Only return user overrides

        Returns:
            List of classification records
        """
        query = "SELECT * FROM workout_ml_classifications WHERE 1=1"
        params = []

        if workout_ids:
            placeholders = ','.join(['%s'] * len(workout_ids))
            query += f" AND workout_id IN ({placeholders})"
            params.extend(workout_ids)

        if model_id:
            query += " AND model_id = %s"
            params.append(model_id)

        if is_override_only:
            query += " AND is_user_override = TRUE"

        try:
            results = self.db_service.execute_query(query, tuple(params))

            # Parse JSON fields
            for result in results:
                if result.get('features_snapshot'):
                    result['features_snapshot'] = json.loads(result['features_snapshot'])
                if result.get('metadata'):
                    result['metadata'] = json.loads(result['metadata'])

            return results

        except Exception as e:
            logger.error(f"Failed to get persisted classifications: {e}")
            return []
