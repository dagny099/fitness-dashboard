# Troubleshooting

This comprehensive troubleshooting guide covers common issues, solutions, and debugging techniques for the Fitness Dashboard.

## Quick Diagnostic Checklist

Before diving into specific issues, run through this basic checklist:

- [ ] **Database Connection**: Can you connect to MySQL?
- [ ] **Environment Variables**: Are all required env vars set?
- [ ] **Dependencies**: Are all Python packages installed?
- [ ] **Port Availability**: Is port 8501 available for Streamlit?
- [ ] **File Permissions**: Can the application read/write necessary files?
- [ ] **Logs**: Check recent logs for error messages

## Installation and Setup Issues

### Poetry and Dependencies

!!! error "Poetry Command Not Found"
    **Error**: `command not found: poetry`
    
    **Cause**: Poetry not installed or not in PATH
    
    **Solutions**:
    ```bash
    # Check if Poetry is installed elsewhere
    find ~ -name poetry 2>/dev/null
    
    # If found, add to PATH
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    
    # If not found, install Poetry
    curl -sSL https://install.python-poetry.org | python3 -
    ```

!!! error "Python Version Compatibility"
    **Error**: `requires python >=3.10, but you have 3.9`
    
    **Solutions**:
    ```bash
    # Check Python version
    python --version
    
    # Install Python 3.10+ (macOS with Homebrew)
    brew install python@3.10
    
    # Update pyproject.toml if needed
    poetry env use python3.10
    poetry install
    ```

!!! error "Lock File Issues"
    **Error**: `poetry.lock is not consistent with pyproject.toml`
    
    **Solutions**:
    ```bash
    # Regenerate lock file
    poetry lock --no-update
    
    # Force update if dependencies changed
    poetry lock
    poetry install
    ```

### Virtual Environment Issues

!!! error "Virtual Environment Not Activated"
    **Symptoms**: Packages not found, wrong Python version
    
    **Solutions**:
    ```bash
    # Check current environment
    which python
    
    # Activate Poetry environment
    poetry shell
    
    # Or use Poetry to run commands
    poetry run python scripts/init.py
    ```

## Database Connection Issues

### MySQL Connection Problems

!!! error "Access Denied for User"
    **Error**: `ERROR 1045 (28000): Access denied for user 'fitness_user'@'localhost'`
    
    **Diagnostic Steps**:
    ```bash
    # Check MySQL service status
    brew services list | grep mysql  # macOS
    sudo systemctl status mysql      # Linux
    
    # Test connection manually
    mysql -u fitness_user -p
    ```
    
    **Solutions**:
    ```sql
    -- Reset user password
    ALTER USER 'fitness_user'@'localhost' IDENTIFIED BY 'new_password';
    FLUSH PRIVILEGES;
    
    -- Or recreate user
    DROP USER IF EXISTS 'fitness_user'@'localhost';
    CREATE USER 'fitness_user'@'localhost' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON sweat.* TO 'fitness_user'@'localhost';
    FLUSH PRIVILEGES;
    ```

!!! error "Can't Connect to MySQL Server"
    **Error**: `ERROR 2002 (HY000): Can't connect to local MySQL server`
    
    **Diagnostic Steps**:
    ```bash
    # Check if MySQL is running
    ps aux | grep mysql
    
    # Check port availability
    netstat -tlnp | grep 3306
    lsof -i :3306
    ```
    
    **Solutions**:
    ```bash
    # Start MySQL service
    brew services start mysql        # macOS
    sudo systemctl start mysql       # Linux
    
    # Check MySQL configuration
    mysql --help | grep "Default options"
    
    # Verify socket file location
    ls -la /tmp/mysql.sock
    ```

!!! error "Database Does Not Exist"
    **Error**: `ERROR 1049 (42000): Unknown database 'sweat'`
    
    **Solution**:
    ```bash
    # Run database initialization
    python scripts/init.py
    
    # Or create manually
    mysql -u root -p -e "CREATE DATABASE sweat;"
    ```

### Environment Configuration Issues

!!! error "Missing Environment Variables"
    **Error**: `KeyError: 'MYSQL_USER'` or similar
    
    **Diagnostic Steps**:
    ```bash
    # Check environment variables
    echo $MYSQL_USER
    printenv | grep MYSQL
    
    # Check .env file exists
    ls -la .env
    cat .env
    ```
    
    **Solutions**:
    ```bash
    # Create .env file
    cat > .env << EOF
    MYSQL_USER=fitness_user
    MYSQL_PWD=your_password
    MYSQL_HOST=localhost
    MYSQL_PORT=3306
    EOF
    
    # Load environment variables
    source .env
    ```

### RDS Connection Issues (Production)

!!! error "RDS Connection Timeout"
    **Error**: Connection timeout when connecting to RDS
    
    **Diagnostic Steps**:
    ```bash
    # Test connectivity
    telnet your-rds-endpoint.amazonaws.com 3306
    
    # Check security groups
    aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
    ```
    
    **Solutions**:
    - Verify security group allows inbound port 3306
    - Check VPC subnet configuration
    - Ensure RDS is publicly accessible if needed
    - Verify endpoint URL is correct

## Streamlit Application Issues

### Application Won't Start

!!! error "Port Already in Use"
    **Error**: `OSError: [Errno 48] Address already in use`
    
    **Diagnostic Steps**:
    ```bash
    # Find process using port 8501
    lsof -i :8501
    netstat -tulpn | grep 8501
    ```
    
    **Solutions**:
    ```bash
    # Kill process using the port
    kill -9 <PID>
    
    # Or use different port
    streamlit run src/streamlit_app.py --server.port 8502
    ```

!!! error "Module Import Errors"
    **Error**: `ModuleNotFoundError: No module named 'src'`
    
    **Diagnostic Steps**:
    ```bash
    # Check current directory
    pwd
    ls -la src/
    
    # Check Python path
    python -c "import sys; print('\n'.join(sys.path))"
    ```
    
    **Solutions**:
    ```bash
    # Ensure you're in project root
    cd /path/to/fitness-dashboard
    
    # Run with Poetry
    poetry run streamlit run src/streamlit_app.py
    
    # Or set PYTHONPATH
    export PYTHONPATH="$PYTHONPATH:$(pwd)"
    ```

### Dashboard Display Issues

!!! error "Empty Dashboard/No Data"
    **Symptoms**: Dashboard loads but shows no workouts
    
    **Diagnostic Steps**:
    ```bash
    # Check database contents
    mysql -u fitness_user -p sweat -e "SELECT COUNT(*) FROM workout_summary;"
    
    # Check for data import issues
    python src/update_db.py
    ```
    
    **Solutions**:
    - Import sample data: `python src/update_db.py`
    - Verify CSV file path in `pyproject.toml`
    - Check database connection in Streamlit

!!! error "Charts Not Displaying"
    **Symptoms**: Chart areas are blank or show errors
    
    **Diagnostic Steps**:
    ```bash
    # Check browser console for JavaScript errors
    # Open browser dev tools (F12) and check console
    
    # Verify Plotly installation
    python -c "import plotly; print(plotly.__version__)"
    ```
    
    **Solutions**:
    ```bash
    # Reinstall Plotly
    poetry add plotly
    
    # Clear Streamlit cache
    # In Streamlit app, press 'C' to clear cache
    
    # Check data format
    # Ensure data contains numeric values for charts
    ```

### Performance Issues

!!! error "Slow Loading Times"
    **Symptoms**: Dashboard takes long time to load or update
    
    **Diagnostic Steps**:
    ```bash
    # Check database query performance
    mysql -u fitness_user -p sweat -e "
    SELECT COUNT(*) FROM workout_summary;
    SHOW PROCESSLIST;
    "
    
    # Monitor system resources
    top
    htop
    ```
    
    **Solutions**:
    ```python
    # Add caching to slow functions
    @st.cache_data(ttl=300)
    def get_monthly_summary():
        return database_service.get_monthly_data()
    
    # Optimize database queries
    # Add date range filters
    # Use indexes on frequently queried columns
    ```

!!! error "Memory Issues"
    **Error**: `MemoryError` or system becomes unresponsive
    
    **Solutions**:
    ```bash
    # Monitor memory usage
    free -h
    
    # Limit data processing
    # Use date range filters
    # Implement pagination
    # Clear Streamlit cache regularly
    ```

## Data Import Issues

### CSV Processing Problems

!!! error "File Not Found"
    **Error**: `FileNotFoundError: [Errno 2] No such file or directory`
    
    **Diagnostic Steps**:
    ```bash
    # Check file exists
    ls -la src/*.csv
    
    # Check pyproject.toml configuration
    grep input_filename pyproject.toml
    ```
    
    **Solutions**:
    ```bash
    # Ensure CSV file is in correct location
    cp your_workout_data.csv src/
    
    # Update pyproject.toml
    [tool.project]
    input_filename = "your_workout_data.csv"
    ```

!!! error "CSV Parsing Errors"
    **Error**: `pandas.errors.ParserError` or encoding issues
    
    **Diagnostic Steps**:
    ```bash
    # Check file encoding
    file -I src/your_data.csv
    
    # View file structure
    head -5 src/your_data.csv
    ```
    
    **Solutions**:
    ```python
    # Handle encoding issues
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    
    # Handle different delimiters
    df = pd.read_csv(filepath, delimiter=';')
    
    # Skip problematic rows
    df = pd.read_csv(filepath, error_bad_lines=False)
    ```

!!! error "Data Validation Failures"
    **Error**: `ValueError: Invalid date format` or similar
    
    **Diagnostic Steps**:
    ```python
    # Check data types
    import pandas as pd
    df = pd.read_csv('src/your_data.csv')
    print(df.dtypes)
    print(df.head())
    ```
    
    **Solutions**:
    ```python
    # Handle date parsing
    df['workout_date'] = pd.to_datetime(df['workout_date'], errors='coerce')
    
    # Clean numeric fields
    df['distance_mi'] = pd.to_numeric(df['distance_mi'], errors='coerce')
    
    # Remove invalid rows
    df = df.dropna(subset=['workout_date', 'activity_type'])
    ```

### Database Import Issues

!!! error "Duplicate Key Errors"
    **Error**: `pymysql.err.IntegrityError: (1062, "Duplicate entry")`
    
    **Solutions**:
    ```sql
    -- Clear existing data before reimport
    DELETE FROM workout_summary;
    
    -- Or use INSERT IGNORE for duplicates
    INSERT IGNORE INTO workout_summary (...) VALUES (...);
    
    -- Or use ON DUPLICATE KEY UPDATE
    INSERT INTO workout_summary (...) VALUES (...)
    ON DUPLICATE KEY UPDATE updated_at = NOW();
    ```

## Production Deployment Issues

### Service Management Problems

!!! error "Systemd Service Won't Start"
    **Error**: Service fails to start or immediately stops
    
    **Diagnostic Steps**:
    ```bash
    # Check service status
    sudo systemctl status fitness-dashboard
    
    # View service logs
    sudo journalctl -u fitness-dashboard -f
    
    # Check service file
    sudo systemctl cat fitness-dashboard
    ```
    
    **Solutions**:
    ```bash
    # Fix common service file issues
    sudo systemctl edit fitness-dashboard
    
    # Ensure correct user and paths
    [Service]
    User=fitness-app
    WorkingDirectory=/home/fitness-app/fitness-dashboard
    EnvironmentFile=/home/fitness-app/.env
    
    # Reload and restart
    sudo systemctl daemon-reload
    sudo systemctl restart fitness-dashboard
    ```

### Nginx Configuration Issues

!!! error "502 Bad Gateway"
    **Error**: Nginx shows 502 error
    
    **Diagnostic Steps**:
    ```bash
    # Check Nginx error logs
    sudo tail -f /var/log/nginx/error.log
    
    # Test Nginx configuration
    sudo nginx -t
    
    # Check if Streamlit is running
    ps aux | grep streamlit
    curl http://localhost:8501
    ```
    
    **Solutions**:
    ```bash
    # Restart services in order
    sudo systemctl restart fitness-dashboard
    sleep 5
    sudo systemctl reload nginx
    
    # Check proxy configuration
    # Ensure proxy_pass points to correct port
    ```

!!! error "SSL Certificate Issues"
    **Error**: SSL certificate warnings or failures
    
    **Diagnostic Steps**:
    ```bash
    # Check certificate status
    sudo certbot certificates
    
    # Test SSL configuration
    openssl s_client -connect workouts.barbhs.com:443
    ```
    
    **Solutions**:
    ```bash
    # Renew certificate
    sudo certbot renew
    
    # Recreate certificate if needed
    sudo certbot delete --cert-name workouts.barbhs.com
    sudo certbot --nginx -d workouts.barbhs.com
    ```

## Performance Troubleshooting

### Database Performance

!!! error "Slow Queries"
    **Symptoms**: Dashboard responds slowly, timeouts
    
    **Diagnostic Steps**:
    ```sql
    -- Enable slow query log
    SET GLOBAL slow_query_log = 'ON';
    SET GLOBAL long_query_time = 2;
    
    -- Check running queries
    SHOW PROCESSLIST;
    
    -- Analyze query performance
    EXPLAIN SELECT * FROM workout_summary WHERE workout_date >= '2024-01-01';
    ```
    
    **Solutions**:
    ```sql
    -- Add appropriate indexes
    CREATE INDEX idx_workout_date ON workout_summary(workout_date);
    CREATE INDEX idx_activity_type ON workout_summary(activity_type);
    
    -- Optimize queries with date ranges
    -- Use LIMIT for large result sets
    -- Consider data archiving for old records
    ```

### Memory and Resource Issues

!!! error "High Memory Usage"
    **Symptoms**: System runs out of memory, applications crash
    
    **Diagnostic Steps**:
    ```bash
    # Monitor memory usage
    free -h
    top -o %MEM
    
    # Check swap usage
    swapon --show
    
    # Monitor specific process
    ps aux --sort=-%mem | head -10
    ```
    
    **Solutions**:
    ```bash
    # Add swap space if needed
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    
    # Optimize application
    # Implement data pagination
    # Use database-level aggregation
    # Clear caches regularly
    ```

## Debugging Techniques

### Application Debugging

**Enable Debug Mode**:
```python
# In Streamlit app
import streamlit as st
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Show debug information
if st.checkbox("Debug Mode"):
    st.write("Session State:", dict(st.session_state))
    st.write("Environment:", os.environ.get("ENVIRONMENT"))
    
    # Test database connection
    try:
        db_service = DatabaseService()
        result = db_service.test_connection()
        st.write("Database Connection:", "✅ OK" if result else "❌ Failed")
    except Exception as e:
        st.error(f"Database Error: {e}")
```

**Log Analysis**:
```bash
# View recent application logs
tail -f /var/log/fitness-dashboard/app.log

# Search for specific errors
grep -i "error\|exception" /var/log/fitness-dashboard/app.log

# Monitor logs in real-time
sudo journalctl -u fitness-dashboard -f

# Filter logs by time
journalctl -u fitness-dashboard --since "2024-01-15 10:00:00"
```

### Network Debugging

**Connection Testing**:
```bash
# Test database connectivity
telnet mysql-host 3306
nc -zv mysql-host 3306

# Test web application
curl -I http://localhost:8501
curl -I https://workouts.barbhs.com

# Check DNS resolution
nslookup workouts.barbhs.com
dig workouts.barbhs.com
```

### Performance Profiling

**Database Profiling**:
```sql
-- Profile query performance
SET profiling = 1;
SELECT * FROM workout_summary WHERE workout_date >= '2024-01-01';
SHOW PROFILES;
SHOW PROFILE FOR QUERY 1;
```

**Python Profiling**:
```python
import cProfile
import pstats

# Profile a specific function
profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = expensive_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Getting Help

### Log Collection

When reporting issues, collect relevant information:

```bash
#!/bin/bash
# collect_debug_info.sh

echo "=== System Information ===" > debug_info.txt
uname -a >> debug_info.txt
python --version >> debug_info.txt

echo -e "\n=== Service Status ===" >> debug_info.txt
systemctl status fitness-dashboard >> debug_info.txt 2>&1

echo -e "\n=== Recent Logs ===" >> debug_info.txt
journalctl -u fitness-dashboard --lines=50 >> debug_info.txt 2>&1

echo -e "\n=== Database Connection ===" >> debug_info.txt
mysql -u fitness_user -p$MYSQL_PWD -e "SELECT COUNT(*) FROM sweat.workout_summary;" >> debug_info.txt 2>&1

echo -e "\n=== Disk Usage ===" >> debug_info.txt
df -h >> debug_info.txt

echo -e "\n=== Memory Usage ===" >> debug_info.txt
free -h >> debug_info.txt
```

### Support Resources

- **GitHub Issues**: [Report bugs and request features](https://github.com/dagny/fitness-dashboard/issues)
- **Email Support**: [barbs@balex.com](mailto:barbs@balex.com)
- **Documentation**: Check other sections of this documentation
- **Community**: Share solutions and get help from other users

### Common Solutions Summary

| Issue Category | Quick Fix | Documentation Link |
|----------------|-----------|-------------------|
| Installation | `poetry install && poetry shell` | [Installation Guide](../getting-started/installation.md) |
| Database Connection | Check MySQL service and credentials | [Database Setup](../getting-started/database-setup.md) |
| Import Issues | Verify CSV file and run `update_db.py` | [Data Import](../user-guide/data-import.md) |
| Performance | Add database indexes and caching | [Architecture](../developer/architecture.md) |
| Production Issues | Check service logs and restart services | [Production Setup](../deployment/production.md) |

Remember: Most issues can be resolved by checking logs, verifying configuration, and ensuring all services are running properly.