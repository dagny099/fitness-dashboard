# Database Setup

This guide covers setting up MySQL for your Fitness Dashboard, including both development and production configurations.

## Development Setup (Local MySQL)

### Install MySQL

=== "macOS (Homebrew)"
    
    ```bash
    # Install MySQL
    brew install mysql
    
    # Start MySQL service
    brew services start mysql
    
    # Secure installation (optional but recommended)
    mysql_secure_installation
    ```

=== "Ubuntu/Debian"
    
    ```bash
    # Update package index
    sudo apt update
    
    # Install MySQL Server
    sudo apt install mysql-server
    
    # Start MySQL service
    sudo systemctl start mysql
    
    # Enable auto-start
    sudo systemctl enable mysql
    
    # Secure installation
    sudo mysql_secure_installation
    ```

=== "Windows"
    
    1. Download MySQL Installer from [mysql.com](https://dev.mysql.com/downloads/installer/)
    2. Run the installer and select "Server only" or "Full" installation
    3. Configure the server during installation
    4. Set root password and create user account

### Create Database User

Connect to MySQL and create a dedicated user for the application:

```sql
-- Connect as root
mysql -u root -p

-- Create database
CREATE DATABASE sweat;

-- Create user (replace 'your_username' and 'your_password')
CREATE USER 'fitness_user'@'localhost' IDENTIFIED BY 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON sweat.* TO 'fitness_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Exit MySQL
EXIT;
```

### Configure Environment Variables

Create or update your `.env` file:

```bash
# Database Configuration
MYSQL_USER=fitness_user
MYSQL_PWD=secure_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=sweat
```

### Initialize Database Schema

Run the initialization script to create tables:

```bash
python scripts/init.py
```

This creates the core table structure:

```sql
CREATE TABLE workout_summary (
    workout_id VARCHAR(20) PRIMARY KEY,
    workout_date DATETIME,
    activity_type VARCHAR(50),
    kcal_burned BIGINT,
    distance_mi FLOAT,
    duration_sec FLOAT,
    avg_pace FLOAT,
    max_pace FLOAT,
    steps BIGINT,
    link VARCHAR(100) 
);
```

## Production Setup (AWS RDS)

For production deployment, the application uses AWS RDS MySQL.

### RDS Instance Setup

1. **Create RDS Instance**:
   - Engine: MySQL 8.0+
   - Instance class: db.t3.micro (or larger based on needs)
   - Storage: 20GB General Purpose SSD
   - Enable automated backups

2. **Security Group Configuration**:
   - Allow inbound MySQL traffic (port 3306) from your application server
   - Restrict access to specific IP addresses or security groups

3. **Parameter Group** (Optional):
   - Create custom parameter group for MySQL tuning
   - Adjust settings like `max_connections`, `innodb_buffer_pool_size`

### Environment Variables (Production)

Set these environment variables on your production server:

```bash
# Production Database Configuration
RDS_ENDPOINT=your-rds-instance.region.rds.amazonaws.com
RDS_USER=admin
RDS_PASSWORD=your-secure-password
RDS_DATABASE=sweat
RDS_PORT=3306
```

### Connection Testing

Test your database connection:

```python
# Test script
import pymysql
import os

try:
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PWD'),
        database='sweat',
        charset='utf8mb4'
    )
    print("✅ Database connection successful!")
    connection.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Database Schema Details

### Core Tables

#### workout_summary
The primary table storing workout data:

| Column | Type | Description |
|--------|------|-------------|
| `workout_id` | VARCHAR(20) | Unique workout identifier |
| `workout_date` | DATETIME | When the workout occurred |
| `activity_type` | VARCHAR(50) | Type of activity (Running, Cycling, etc.) |
| `kcal_burned` | BIGINT | Calories burned during workout |
| `distance_mi` | FLOAT | Distance covered in miles |
| `duration_sec` | FLOAT | Workout duration in seconds |
| `avg_pace` | FLOAT | Average pace (min/mile) |
| `max_pace` | FLOAT | Best pace achieved |
| `steps` | BIGINT | Step count (if available) |
| `link` | VARCHAR(100) | Link to original workout data |

### Indexes

For optimal performance, consider adding indexes:

```sql
-- Index for date-based queries
CREATE INDEX idx_workout_date ON workout_summary(workout_date);

-- Index for activity type filtering
CREATE INDEX idx_activity_type ON workout_summary(activity_type);

-- Composite index for common queries
CREATE INDEX idx_date_activity ON workout_summary(workout_date, activity_type);
```

## Data Migration

### From MapMyRun

1. Export your data from [MapMyRun Export](https://www.mapmyfitness.com/workout/export/csv)
2. Place CSV in `src/` directory
3. Update file reference in `pyproject.toml`:

```toml
[tool.project]
input_filename = "your_workout_history.csv"
```

4. Run migration:

```bash
python src/update_db.py
```

### Custom Data Sources

For other fitness platforms, ensure your CSV includes these columns:

- Workout ID or Date (for uniqueness)
- Date/Time
- Activity Type
- Calories
- Distance
- Duration

The application can be extended to handle different CSV formats by modifying `src/update_db.py`.

## Backup and Maintenance

### Backup Strategy

```bash
# Create backup
mysqldump -u fitness_user -p sweat > backup_$(date +%Y%m%d).sql

# Restore from backup
mysql -u fitness_user -p sweat < backup_20240115.sql
```

### Maintenance Tasks

Regular maintenance for optimal performance:

```sql
-- Analyze table statistics
ANALYZE TABLE workout_summary;

-- Optimize table
OPTIMIZE TABLE workout_summary;

-- Check table integrity
CHECK TABLE workout_summary;
```

## Troubleshooting

### Common Connection Issues

!!! error "Access Denied"
    ```
    ERROR 1045 (28000): Access denied for user 'fitness_user'@'localhost'
    ```
    **Solution**: Verify username/password and user permissions

!!! error "Can't Connect to Server"
    ```
    ERROR 2002 (HY000): Can't connect to local MySQL server
    ```
    **Solutions**:
    - Check if MySQL service is running: `sudo systemctl status mysql`
    - Verify port 3306 is not blocked: `netstat -tlnp | grep 3306`

!!! error "Database Doesn't Exist"
    ```
    ERROR 1049 (42000): Unknown database 'sweat'
    ```
    **Solution**: Run `python scripts/init.py` to create the database

### Performance Issues

- **Slow Queries**: Add appropriate indexes for your query patterns
- **Connection Timeouts**: Increase `wait_timeout` in MySQL configuration
- **Memory Usage**: Tune `innodb_buffer_pool_size` based on available RAM

For more help, see [Troubleshooting Reference](../reference/troubleshooting.md).