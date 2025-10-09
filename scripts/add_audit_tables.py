"""
Database Migration: Add Audit History and Model Versioning Tables

This script creates the necessary database tables for:
1. Classification audit history tracking
2. ML model version management
3. User feedback collection

Usage:
    python scripts/add_audit_tables.py

Pre-requisites:
    - Database must already exist (run scripts/init.py first)
    - Environment variables set (MYSQL_USER, MYSQL_PWD or RDS credentials)
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import logging
from src.config.database import DatabaseConfig
from src.services.database_service import DatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL schemas for new tables
AUDIT_TABLES_SCHEMA = {

    # Table 1: Classification Audit History
    "workout_classification_history": """
        CREATE TABLE IF NOT EXISTS workout_classification_history (
            history_id INT AUTO_INCREMENT PRIMARY KEY,
            workout_id VARCHAR(20) NOT NULL,

            -- Classification details
            previous_classification VARCHAR(50),
            new_classification VARCHAR(50) NOT NULL,
            classification_source ENUM(
                'csv_import',
                'ml_prediction',
                'ml_batch_update',
                'user_override',
                'admin_correction',
                'era_fallback'
            ) NOT NULL,
            classification_confidence FLOAT DEFAULT NULL,
            classification_method VARCHAR(100),

            -- Model versioning
            model_id VARCHAR(100),
            model_version VARCHAR(20),

            -- Audit metadata
            changed_by VARCHAR(100) DEFAULT 'system',
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reason TEXT,

            -- Additional context
            features_used JSON,
            metadata JSON,

            -- Indexes for performance
            INDEX idx_workout_id (workout_id),
            INDEX idx_changed_at (changed_at),
            INDEX idx_model_id (model_id),
            INDEX idx_source (classification_source),

            -- Foreign key constraint
            FOREIGN KEY (workout_id) REFERENCES workout_summary(workout_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,

    # Table 2: ML Model Version Registry
    "ml_model_registry": """
        CREATE TABLE IF NOT EXISTS ml_model_registry (
            registry_id INT AUTO_INCREMENT PRIMARY KEY,

            -- Model identification
            model_id VARCHAR(100) UNIQUE NOT NULL,
            model_name VARCHAR(100) NOT NULL,
            model_version VARCHAR(20) NOT NULL,

            -- Model status
            status ENUM('training', 'active', 'archived', 'deprecated', 'failed') NOT NULL DEFAULT 'training',
            is_production BOOLEAN DEFAULT FALSE,

            -- Training metadata
            trained_at TIMESTAMP NULL,
            activated_at TIMESTAMP NULL,
            archived_at TIMESTAMP NULL,
            training_duration_sec INT,

            -- Dataset information
            training_workouts_count INT,
            training_date_start DATE,
            training_date_end DATE,
            training_features JSON,

            -- Performance metrics
            silhouette_score FLOAT,
            inertia FLOAT,
            cluster_distribution JSON,
            confidence_stats JSON,

            -- Model parameters
            n_clusters INT DEFAULT 3,
            algorithm_type VARCHAR(50) DEFAULT 'kmeans',
            hyperparameters JSON,

            -- Activity type mapping
            cluster_to_activity_map JSON NOT NULL,
            activity_type_stats JSON,

            -- File references
            model_file_path VARCHAR(500),
            metadata_file_path VARCHAR(500),

            -- Versioning and tracking
            parent_model_id VARCHAR(100),
            created_by VARCHAR(100) DEFAULT 'system',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

            -- Notes and documentation
            training_notes TEXT,
            performance_notes TEXT,

            -- Indexes
            INDEX idx_model_id (model_id),
            INDEX idx_status (status),
            INDEX idx_is_production (is_production),
            INDEX idx_trained_at (trained_at),
            INDEX idx_version (model_version),

            -- Foreign key for model lineage
            FOREIGN KEY (parent_model_id) REFERENCES ml_model_registry(model_id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,

    # Table 3: User Classification Feedback
    "user_classification_feedback": """
        CREATE TABLE IF NOT EXISTS user_classification_feedback (
            feedback_id INT AUTO_INCREMENT PRIMARY KEY,

            -- Workout and classification
            workout_id VARCHAR(20) NOT NULL,
            ai_classification VARCHAR(50) NOT NULL,
            ai_confidence FLOAT,
            user_classification VARCHAR(50),

            -- Feedback details
            feedback_type ENUM('accept', 'reject', 'correct', 'uncertain') NOT NULL,
            user_certainty INT,  -- 1-5 scale
            comments TEXT,

            -- Context
            model_id VARCHAR(100),
            classification_method VARCHAR(100),

            -- User metadata
            user_id VARCHAR(100),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),

            -- Processing status
            processed BOOLEAN DEFAULT FALSE,
            processed_at TIMESTAMP NULL,
            incorporated_in_model VARCHAR(100),

            -- Indexes
            INDEX idx_workout_id (workout_id),
            INDEX idx_feedback_type (feedback_type),
            INDEX idx_processed (processed),
            INDEX idx_model_id (model_id),
            INDEX idx_submitted_at (submitted_at),

            -- Foreign keys
            FOREIGN KEY (workout_id) REFERENCES workout_summary(workout_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (model_id) REFERENCES ml_model_registry(model_id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,

    # Table 4: Classification Persistence (optional - for persisting ML predictions)
    "workout_ml_classifications": """
        CREATE TABLE IF NOT EXISTS workout_ml_classifications (
            classification_id INT AUTO_INCREMENT PRIMARY KEY,

            -- Workout reference
            workout_id VARCHAR(20) NOT NULL,

            -- Current active classification
            current_classification VARCHAR(50) NOT NULL,
            classification_source VARCHAR(100) NOT NULL,
            classification_confidence FLOAT,
            classification_method VARCHAR(100),

            -- Model reference
            model_id VARCHAR(100),
            model_version VARCHAR(20),

            -- User override tracking
            is_user_override BOOLEAN DEFAULT FALSE,
            original_ml_classification VARCHAR(50),
            override_reason TEXT,

            -- Timestamps
            classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

            -- Change tracking
            classification_change_count INT DEFAULT 0,

            -- Metadata
            features_snapshot JSON,
            metadata JSON,

            -- Indexes
            UNIQUE KEY unique_workout (workout_id),
            INDEX idx_model_id (model_id),
            INDEX idx_classification (current_classification),
            INDEX idx_is_override (is_user_override),
            INDEX idx_classified_at (classified_at),

            -- Foreign keys
            FOREIGN KEY (workout_id) REFERENCES workout_summary(workout_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (model_id) REFERENCES ml_model_registry(model_id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
}

def create_audit_tables():
    """Create all audit and versioning tables."""
    logger.info("=" * 60)
    logger.info("Creating Audit History and Model Versioning Tables")
    logger.info("=" * 60)

    # Initialize database service
    db_config = DatabaseConfig.from_environment()
    db_service = DatabaseService(db_config)

    # Test connection
    if not db_service.test_connection():
        logger.error("❌ Database connection failed. Cannot proceed.")
        return False

    logger.info("✅ Database connection successful")

    # Create each table
    success_count = 0
    for table_name, schema in AUDIT_TABLES_SCHEMA.items():
        try:
            logger.info(f"\nCreating table: {table_name}...")

            with db_service.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(schema)
                    connection.commit()

            logger.info(f"✅ Table '{table_name}' created successfully")
            success_count += 1

        except Exception as e:
            logger.error(f"❌ Failed to create table '{table_name}': {e}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info(f"Migration Summary: {success_count}/{len(AUDIT_TABLES_SCHEMA)} tables created")
    logger.info("=" * 60)

    if success_count == len(AUDIT_TABLES_SCHEMA):
        logger.info("🎉 All audit tables created successfully!")
        return True
    else:
        logger.warning(f"⚠️ Some tables failed to create. Check logs above.")
        return False

def verify_tables():
    """Verify that all tables were created correctly."""
    logger.info("\nVerifying table creation...")

    db_config = DatabaseConfig.from_environment()
    db_service = DatabaseService(db_config)

    try:
        with db_service.get_connection() as connection:
            with connection.cursor() as cursor:
                for table_name in AUDIT_TABLES_SCHEMA.keys():
                    # Check if table exists
                    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                    result = cursor.fetchone()

                    if result:
                        # Get table info
                        cursor.execute(f"DESCRIBE {table_name}")
                        columns = cursor.fetchall()
                        logger.info(f"✅ Table '{table_name}' verified - {len(columns)} columns")
                    else:
                        logger.error(f"❌ Table '{table_name}' not found")

        return True

    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

def main():
    """Main migration execution."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  Fitness Dashboard - Audit Tables Migration             ║")
    print("║  Version: 1.0.0                                          ║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    # Ask for confirmation
    response = input("This will create 4 new tables in your database. Continue? (y/n): ")
    if response.lower() != 'y':
        logger.info("Migration cancelled by user.")
        return

    # Create tables
    if create_audit_tables():
        # Verify tables
        verify_tables()

        logger.info("\n✅ Migration completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Update DatabaseService to use new audit logging methods")
        logger.info("2. Update ModelManager to register models in ml_model_registry")
        logger.info("3. Implement user override UI with feedback collection")
        logger.info("4. Run initial ML classification batch update")
    else:
        logger.error("\n❌ Migration completed with errors. Please review logs.")

if __name__ == "__main__":
    main()
