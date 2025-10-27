# Local Development

This guide covers setting up and running the Fitness Dashboard in a local development environment.

## Development Environment Setup

### Prerequisites

Ensure you have the following installed on your development machine:

- **Python 3.10+**: Download from [python.org](https://python.org)
- **Poetry**: For dependency management
- **MySQL 8.0+**: Local database server
- **Git**: For version control

### Quick Setup

Follow these steps to get your development environment running:

```bash
# Clone the repository
git clone https://github.com/dagny099/fitness-dashboard.git
cd fitness-dashboard

# Install dependencies with Poetry
poetry install

# Activate the virtual environment
poetry shell

# Initialize the database
python scripts/init.py

# Start the development server
streamlit run src/streamlit_app.py
```

Visit `http://localhost:8501` to access your development dashboard.

## Development Workflow

### Directory Structure

Understanding the project structure helps with efficient development:

```
fitness-dashboard/
├── src/                    # Main source code
│   ├── config/            # Configuration files
│   ├── services/          # Business logic
│   ├── utils/             # Shared utilities
│   ├── views/             # UI components
│   └── streamlit_app.py   # Entry point
├── docs/                  # Documentation (MkDocs)
├── tests/                 # Test suite
├── scripts/               # Setup/deployment scripts
└── pyproject.toml         # Project configuration
```

### Environment Variables

Create a `.env` file in the project root for local development:

```bash
# Database Configuration
MYSQL_USER=fitness_user
MYSQL_PWD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=sweat

# Application Settings
STREAMLIT_THEME=dark
DEBUG=true

# Optional: Enable additional logging
LOG_LEVEL=DEBUG
```

### Configuration Management

The application automatically detects the development environment:

```python
# src/config/app.py
def get_environment():
    """Detects macOS as development environment"""
    return "development" if platform.system() == "Darwin" else "production"
```

This enables:
- Local MySQL connection
- Debug logging
- Development-specific features
- Hot reload capabilities

## Development Tools

### Code Quality Tools

Set up code quality tools for consistent development:

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Code formatting (if configured)
poetry run black src/
poetry run isort src/

# Type checking (if mypy is added)
poetry run mypy src/
```

### Database Development

#### Local MySQL Setup

**macOS (Homebrew)**:
```bash
brew install mysql
brew services start mysql

# Create development database
mysql -u root -p
CREATE DATABASE sweat;
CREATE USER 'fitness_user'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON sweat.* TO 'fitness_user'@'localhost';
FLUSH PRIVILEGES;
```

**Database Management**:
```bash
# Initialize schema
python scripts/init.py

# Import sample data
python scripts/update_db.py

# Reset database (if needed)
mysql -u fitness_user -p sweat < scripts/reset_db.sql
```

!!! important "Set the environment"
    On Linux or Windows, export `FITNESS_DASHBOARD_ENV=development` before running local scripts so the app connects with the credentials defined here. Otherwise it will expect `RDS_*` variables for a remote database.

#### Database Tools

Recommended tools for database development:

- **MySQL Workbench**: GUI for database management
- **DBeaver**: Universal database tool
- **phpMyAdmin**: Web-based MySQL administration

### Streamlit Development

#### Hot Reload

Streamlit provides automatic reloading when files change:

```bash
# Start with file watcher (default behavior)
streamlit run src/streamlit_app.py

# The app automatically reloads when you save changes
```

#### Debug Mode

Enable additional debugging features:

```python
# In your Streamlit app
import streamlit as st

# Display session state for debugging
if st.checkbox("Show Debug Info"):
    st.write("Session State:", st.session_state)
    st.write("Environment:", AppConfig.get_environment())
```

#### Development Server Options

```bash
# Run on different port
streamlit run src/streamlit_app.py --server.port 8502

# Enable CORS for external access
streamlit run src/streamlit_app.py --server.enableCORS false

# Disable file watching (for performance)
streamlit run src/streamlit_app.py --server.fileWatcherType none
```

## Testing During Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test file
poetry run pytest tests/test_queries.py

# Run with verbose output
poetry run pytest -v

# Run tests in parallel (if pytest-xdist is installed)
poetry run pytest -n auto
```

### Test Database

Set up a separate test database:

```sql
CREATE DATABASE sweat_test;
GRANT ALL PRIVILEGES ON sweat_test.* TO 'fitness_user'@'localhost';
```

Configure test environment:

```python
# tests/conftest.py
import pytest
from src.services.database_service import DatabaseService

@pytest.fixture(scope="session")
def test_db():
    """Test database fixture"""
    # Setup test database
    # Import test data
    yield database_service
    # Cleanup
```

### Manual Testing

Create test scenarios for manual verification:

```python
# scripts/create_test_data.py
def create_sample_workouts():
    """Generate sample workout data for testing"""
    sample_data = [
        {
            "workout_id": "test_001",
            "workout_date": datetime.now() - timedelta(days=1),
            "activity_type": "Running",
            "kcal_burned": 450,
            "distance_mi": 3.1,
            "duration_sec": 1860
        },
        # Add more test data...
    ]
    
    db_service = DatabaseService()
    db_service.bulk_insert("workout_summary", sample_data)
    print(f"Inserted {len(sample_data)} test workouts")

if __name__ == "__main__":
    create_sample_workouts()
```

## Debugging

### Streamlit Debugging

**Debug Information Display**:
```python
# Add to your Streamlit pages
if st.sidebar.checkbox("Debug Mode"):
    st.sidebar.write("Session State:", dict(st.session_state))
    st.sidebar.write("Current User:", get_current_user())
    st.sidebar.write("Database Status:", test_db_connection())
```

**Error Handling**:
```python
try:
    data = database_service.execute_query(query)
    st.dataframe(data)
except Exception as e:
    st.error(f"Query failed: {str(e)}")
    if st.checkbox("Show full error"):
        st.exception(e)
```

### Database Debugging

**Query Logging**:
```python
# Enable query logging in development
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("database")

def execute_query_with_logging(query, params=None):
    logger.debug(f"Executing query: {query}")
    logger.debug(f"Parameters: {params}")
    # ... execute query
```

**Performance Monitoring**:
```python
import time
from functools import wraps

def monitor_db_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > 1.0:  # Log slow queries
            logger.warning(f"Slow query ({execution_time:.2f}s): {func.__name__}")
        
        return result
    return wrapper
```

## Development Best Practices

### Code Organization

**Module Structure**:
- Keep related functionality together
- Use clear, descriptive names
- Maintain separation of concerns
- Document complex functions

**Error Handling**:
```python
# Consistent error handling pattern
def safe_database_operation():
    try:
        return database_service.execute_query(query)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        st.error("Database connection issue. Please try again.")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        st.error("An unexpected error occurred.")
        return []
```

### Performance Considerations

**Caching Strategy**:
```python
import streamlit as st

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_monthly_summary(month):
    """Cached data retrieval for better performance"""
    return database_service.get_monthly_data(month)
```

**Efficient Queries**:
```python
# Use date range filters for large datasets
def get_recent_workouts(days=30):
    query = """
    SELECT * FROM workout_summary 
    WHERE workout_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
    ORDER BY workout_date DESC
    """
    return database_service.execute_query(query, (days,))
```

### Version Control

**Git Workflow**:
```bash
# Create feature branch
git checkout -b feature/new-visualization

# Make changes and commit frequently
git add .
git commit -m "Add new chart type for pace analysis"

# Push to remote
git push origin feature/new-visualization

# Create pull request when ready
```

**Ignore Files**:
Ensure your `.gitignore` includes:
```
# Environment files
.env
.env.local

# Database files
*.db
sessions.db

# IDE files
.vscode/
.idea/

# Python cache
__pycache__/
*.pyc

# Streamlit cache
.streamlit/
```

## Troubleshooting Development Issues

### Common Problems

!!! error "Port Already in Use"
    **Error**: `Address already in use`
    
    **Solutions**:
    ```bash
    # Find process using port 8501
    lsof -i :8501
    
    # Kill the process
    kill -9 <PID>
    
    # Or use a different port
    streamlit run src/streamlit_app.py --server.port 8502
    ```

!!! error "Database Connection Failed"
    **Error**: `Can't connect to MySQL server`
    
    **Solutions**:
    ```bash
    # Check MySQL status
    brew services list | grep mysql
    
    # Start MySQL if stopped
    brew services start mysql
    
    # Verify credentials
    mysql -u fitness_user -p sweat
    ```

!!! error "Module Import Errors"
    **Error**: `ModuleNotFoundError`
    
    **Solutions**:
    ```bash
    # Ensure you're in the poetry environment
    poetry shell
    
    # Reinstall dependencies
    poetry install
    
    # Check Python path
    python -c "import sys; print(sys.path)"
    ```

### Performance Issues

**Slow Dashboard Loading**:
- Check database query performance
- Implement data caching
- Reduce dataset size for development
- Use pagination for large results

**Memory Usage**:
- Monitor Streamlit session state size
- Clear unused cached data
- Implement data cleanup routines

## Documentation Development

### MkDocs Development

```bash
# Install documentation dependencies (already included)
poetry install

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build

# Open in browser
open http://localhost:8000
```

### Documentation Best Practices

- Keep documentation up to date with code changes
- Include code examples in docstrings
- Write clear user guides for new features
- Test documentation links regularly

## Next Steps

Once your development environment is set up:

1. **Explore the Codebase**: Understand the architecture and existing patterns
2. **Run Tests**: Ensure everything works correctly
3. **Make Your First Change**: Start with a small improvement or bug fix
4. **Follow the Style Guide**: Maintain consistency with existing code
5. **Write Tests**: Add tests for new functionality
6. **Update Documentation**: Keep docs current with changes

For production deployment, see the [Production Setup Guide](production.md).