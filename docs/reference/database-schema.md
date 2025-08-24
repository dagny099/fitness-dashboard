# Database Schema

This document provides detailed information about the Fitness Dashboard database schema, including table structures, relationships, and indexing strategies.

## Overview

The Fitness Dashboard uses a MySQL database with a straightforward schema optimized for fitness tracking and analytics. The current implementation focuses on a single core table with plans for future expansion.

### Database Information

- **Database Name**: `sweat`
- **Engine**: MySQL 8.0+
- **Character Set**: utf8mb4
- **Collation**: utf8mb4_unicode_ci

## Core Tables

### workout_summary

The primary table storing all workout data imported from fitness platforms.

#### Table Definition

```sql
CREATE TABLE workout_summary (
    workout_id VARCHAR(20) PRIMARY KEY,
    workout_date DATETIME NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    kcal_burned BIGINT,
    distance_mi FLOAT,
    duration_sec FLOAT,
    avg_pace FLOAT,
    max_pace FLOAT,
    steps BIGINT,
    link VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### Column Specifications

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `workout_id` | VARCHAR(20) | NO | | Unique identifier for the workout (Primary Key) |
| `workout_date` | DATETIME | NO | | Date and time when the workout occurred |
| `activity_type` | VARCHAR(50) | NO | | Type of physical activity (Running, Cycling, etc.) |
| `kcal_burned` | BIGINT | YES | NULL | Total calories burned during the workout |
| `distance_mi` | FLOAT | YES | NULL | Distance covered in miles |
| `duration_sec` | FLOAT | YES | NULL | Workout duration in seconds |
| `avg_pace` | FLOAT | YES | NULL | Average pace in minutes per mile |
| `max_pace` | FLOAT | YES | NULL | Best/fastest pace achieved in minutes per mile |
| `steps` | BIGINT | YES | NULL | Total step count (if available) |
| `link` | VARCHAR(100) | YES | NULL | URL to original workout data |
| `created_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Last update timestamp |

#### Data Types and Constraints

**Primary Key**:
- `workout_id`: Must be unique across all records
- Typically sourced from fitness platform's workout identifier
- Maximum 20 characters to accommodate various ID formats

**Required Fields**:
- `workout_date`: Must be a valid datetime
- `activity_type`: Cannot be empty, standardized activity names

**Numeric Fields**:
- `kcal_burned`: BIGINT to handle high-calorie workouts
- `distance_mi`: FLOAT with precision for decimal miles
- `duration_sec`: FLOAT to handle fractional seconds
- `pace fields`: FLOAT for precise pace calculations
- `steps`: BIGINT for high step counts

**Text Fields**:
- `activity_type`: Limited to 50 characters
- `link`: Limited to 100 characters for URLs

## Indexes

### Performance Indexes

Indexes are crucial for query performance, especially with large datasets:

```sql
-- Primary index (automatic)
PRIMARY KEY (workout_id)

-- Date-based queries (most common)
CREATE INDEX idx_workout_date ON workout_summary(workout_date);

-- Activity filtering
CREATE INDEX idx_activity_type ON workout_summary(activity_type);

-- Composite index for common query patterns
CREATE INDEX idx_date_activity ON workout_summary(workout_date, activity_type);

-- Performance metrics queries
CREATE INDEX idx_distance_date ON workout_summary(distance_mi, workout_date);
CREATE INDEX idx_calories_date ON workout_summary(kcal_burned, workout_date);
```

### Index Usage Patterns

**Date Range Queries**:
```sql
-- Uses idx_workout_date
SELECT * FROM workout_summary 
WHERE workout_date >= '2024-01-01' 
  AND workout_date < '2024-02-01';
```

**Activity Analysis**:
```sql
-- Uses idx_date_activity composite index
SELECT activity_type, COUNT(*), AVG(distance_mi)
FROM workout_summary 
WHERE workout_date >= '2024-01-01'
GROUP BY activity_type;
```

**Performance Queries**:
```sql
-- Uses idx_distance_date for efficient filtering
SELECT * FROM workout_summary 
WHERE distance_mi > 5.0 
  AND workout_date >= '2024-01-01'
ORDER BY distance_mi DESC;
```

## Data Validation Rules

### Application-Level Constraints

The application enforces additional validation beyond database constraints:

#### Workout ID Validation
```python
def validate_workout_id(workout_id: str) -> bool:
    """Validate workout ID format"""
    return (
        workout_id and 
        len(workout_id) <= 20 and 
        workout_id.isalnum()
    )
```

#### Date Validation
```python
def validate_workout_date(date: datetime) -> bool:
    """Validate workout date is reasonable"""
    now = datetime.now()
    min_date = datetime(2000, 1, 1)  # Reasonable minimum
    return min_date <= date <= now
```

#### Numeric Field Validation
```python
def validate_numeric_fields(workout_data: dict) -> dict:
    """Validate and clean numeric fields"""
    validations = {
        'kcal_burned': lambda x: 0 <= x <= 10000,  # Reasonable calorie range
        'distance_mi': lambda x: 0 <= x <= 200,    # Max reasonable distance
        'duration_sec': lambda x: 60 <= x <= 86400, # 1 min to 24 hours
        'avg_pace': lambda x: 3 <= x <= 30,        # 3-30 min/mile reasonable
        'max_pace': lambda x: 3 <= x <= 30,        # Same range as avg_pace
        'steps': lambda x: 0 <= x <= 100000        # Max reasonable steps
    }
    # Apply validations and clean data
    return cleaned_data
```

## Common Query Patterns

### Performance Optimized Queries

#### Monthly Summaries
```sql
-- Optimized monthly aggregation
SELECT 
    DATE_FORMAT(workout_date, '%Y-%m') as month,
    COUNT(*) as total_workouts,
    ROUND(SUM(distance_mi), 2) as total_distance,
    ROUND(SUM(kcal_burned)) as total_calories,
    ROUND(AVG(duration_sec / 60), 1) as avg_duration_min
FROM workout_summary
WHERE workout_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY DATE_FORMAT(workout_date, '%Y-%m')
ORDER BY month DESC;
```

#### Activity Performance Analysis
```sql
-- Activity-specific performance metrics
SELECT 
    activity_type,
    COUNT(*) as workout_count,
    ROUND(AVG(distance_mi), 2) as avg_distance,
    ROUND(AVG(kcal_burned)) as avg_calories,
    ROUND(AVG(avg_pace), 2) as avg_pace,
    ROUND(MIN(avg_pace), 2) as best_pace
FROM workout_summary
WHERE workout_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
  AND distance_mi > 0
  AND avg_pace IS NOT NULL
GROUP BY activity_type
HAVING workout_count >= 5  -- Only activities with sufficient data
ORDER BY workout_count DESC;
```

#### Recent Activity Trends
```sql
-- Recent workout trends with rolling averages
SELECT 
    workout_date,
    activity_type,
    distance_mi,
    kcal_burned,
    AVG(distance_mi) OVER (
        ORDER BY workout_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as rolling_avg_distance
FROM workout_summary
WHERE workout_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY workout_date DESC;
```

## Data Import Schema Mapping

### CSV to Database Mapping

The application maps CSV columns from fitness platforms to database fields:

| CSV Column (MapMyRun) | Database Field | Transformation |
|----------------------|----------------|----------------|
| Workout Id | workout_id | Direct mapping |
| Workout Date | workout_date | Parse datetime string |
| Activity Type | activity_type | Standardize activity names |
| Total Calories | kcal_burned | Convert to integer |
| Distance (mi) | distance_mi | Convert to float |
| Duration | duration_sec | Convert time to seconds |
| Avg Pace (min/mi) | avg_pace | Convert to float |
| Max Pace (min/mi) | max_pace | Convert to float |
| Steps | steps | Convert to integer |
| Reference | link | Direct mapping |

### Data Transformation Logic

```python
def transform_csv_row(row: dict) -> dict:
    """Transform CSV row to database format"""
    return {
        'workout_id': row['Workout Id'],
        'workout_date': parse_datetime(row['Workout Date']),
        'activity_type': standardize_activity_type(row['Activity Type']),
        'kcal_burned': safe_int_conversion(row.get('Total Calories')),
        'distance_mi': safe_float_conversion(row.get('Distance (mi)')),
        'duration_sec': parse_duration(row.get('Duration')),
        'avg_pace': safe_float_conversion(row.get('Avg Pace (min/mi)')),
        'max_pace': safe_float_conversion(row.get('Max Pace (min/mi)')),
        'steps': safe_int_conversion(row.get('Steps')),
        'link': row.get('Reference'),
    }
```

## Database Maintenance

### Regular Maintenance Tasks

#### Data Cleanup
```sql
-- Remove duplicate workouts (keep most recent)
DELETE w1 FROM workout_summary w1
INNER JOIN workout_summary w2 
WHERE w1.workout_id = w2.workout_id 
  AND w1.created_at < w2.created_at;

-- Clean invalid data
UPDATE workout_summary 
SET distance_mi = NULL 
WHERE distance_mi < 0 OR distance_mi > 200;

UPDATE workout_summary 
SET kcal_burned = NULL 
WHERE kcal_burned < 0 OR kcal_burned > 10000;
```

#### Index Maintenance
```sql
-- Analyze table statistics
ANALYZE TABLE workout_summary;

-- Optimize table structure
OPTIMIZE TABLE workout_summary;

-- Check table integrity
CHECK TABLE workout_summary;

-- Rebuild indexes if needed
ALTER TABLE workout_summary ENGINE=InnoDB;
```

#### Performance Monitoring
```sql
-- Check index usage
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    CARDINALITY,
    INDEX_TYPE
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'sweat' 
  AND TABLE_NAME = 'workout_summary';

-- Monitor slow queries (enable slow query log)
SELECT 
    query_time,
    lock_time,
    rows_sent,
    rows_examined,
    sql_text
FROM mysql.slow_log 
WHERE start_time >= DATE_SUB(NOW(), INTERVAL 1 DAY);
```

## Future Schema Evolution

### Planned Enhancements

#### User Management
```sql
-- Future user table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add user reference to workouts
ALTER TABLE workout_summary 
ADD COLUMN user_id UUID,
ADD FOREIGN KEY (user_id) REFERENCES users(user_id);
```

#### Goal Tracking
```sql
-- Goals and targets table
CREATE TABLE fitness_goals (
    goal_id UUID PRIMARY KEY,
    user_id UUID,
    goal_type ENUM('distance', 'calories', 'workouts', 'pace'),
    target_value FLOAT NOT NULL,
    target_period ENUM('daily', 'weekly', 'monthly', 'yearly'),
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### Workout Details
```sql
-- Detailed workout metrics
CREATE TABLE workout_metrics (
    metric_id UUID PRIMARY KEY,
    workout_id VARCHAR(20),
    metric_type VARCHAR(30) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(10),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workout_id) REFERENCES workout_summary(workout_id)
);
```

### Migration Strategy

For schema changes, use versioned migration scripts:

```sql
-- migrations/001_add_user_support.sql
-- Migration: Add user support to workout_summary
-- Date: 2024-XX-XX

START TRANSACTION;

-- Add user_id column
ALTER TABLE workout_summary 
ADD COLUMN user_id UUID DEFAULT NULL;

-- Create index for user queries
CREATE INDEX idx_user_workouts ON workout_summary(user_id, workout_date);

-- Update version
INSERT INTO schema_migrations (version, description, applied_at) 
VALUES (1, 'Add user support', NOW());

COMMIT;
```

## Backup and Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup_database.sh

DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/path/to/backups"
DB_NAME="sweat"

# Full database backup
mysqldump -u fitness_user -p$MYSQL_PWD \
  --single-transaction \
  --routines \
  --triggers \
  $DB_NAME > $BACKUP_DIR/sweat_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/sweat_backup_$DATE.sql

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "sweat_backup_*.sql.gz" -mtime +30 -delete
```

### Recovery Procedures

```bash
# Restore from backup
gunzip sweat_backup_20240115_120000.sql.gz
mysql -u fitness_user -p sweat < sweat_backup_20240115_120000.sql

# Verify restoration
mysql -u fitness_user -p -e "
  SELECT COUNT(*) as total_workouts,
         MIN(workout_date) as earliest,
         MAX(workout_date) as latest
  FROM sweat.workout_summary;"
```

For more information about database operations, see the [API Reference](../developer/api-reference.md).