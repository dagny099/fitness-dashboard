# Fitness Dashboard - Architecture Documentation

## Project Structure

The project has been reorganized for better maintainability and scalability:

```
fitness-dashboard/
├── src/
│   ├── config/              # Configuration management
│   │   ├── __init__.py
│   │   ├── app.py          # Application configuration
│   │   ├── database.py     # Database configuration
│   │   └── logging_config.py # Logging setup
│   ├── models/             # Data models (future expansion)
│   ├── services/           # Business logic layer
│   │   ├── __init__.py
│   │   └── database_service.py # Centralized database operations
│   ├── utils/              # Shared utilities
│   │   ├── __init__.py
│   │   ├── session_manager.py
│   │   ├── storage.py
│   │   └── utilities.py    # Helper functions with type hints
│   ├── views/              # Streamlit pages and components
│   │   ├── __init__.py
│   │   ├── dash.py         # Monthly dashboard view
│   │   ├── fitness-overview.py # SQL query interface
│   │   ├── login.py        # Authentication page
│   │   ├── calendar_more.py # Detailed statistics
│   │   └── tools/          # Additional tools and utilities
│   │       ├── history.py
│   │       ├── mapping.py
│   │       ├── testcard.py
│   │       └── trends.py
│   ├── streamlit_app.py    # Main application entry point
│   └── other legacy files...
├── scripts/                # Setup and deployment scripts
│   ├── init.py            # Database initialization
│   └── deploy.sh          # Production deployment
├── tests/                  # Test suite
└── documentation files...
```

## Key Improvements

### 1. **Centralized Configuration**
- `src/config/database.py`: Environment-aware database configuration
- `src/config/app.py`: Application settings and style configuration  
- `src/config/logging_config.py`: Structured logging setup

### 2. **Database Service Layer**
- `src/services/database_service.py`: Consolidated database operations
- Connection management with context managers
- Error handling and logging
- Environment-specific configuration

### 3. **Type Safety**
- Added type hints throughout the codebase
- Proper imports with relative path structure
- Enhanced error handling

### 4. **Improved Logging**
- Structured logging with appropriate levels
- Centralized logger configuration
- Better error reporting and debugging

### 5. **Code Organization**
- Clear separation of concerns (config, services, views, utils)
- Consistent import patterns
- Deprecated API fixes (st.experimental_rerun → st.rerun)

## Usage

### Development Setup
```bash
# Run database initialization
python scripts/init.py

# Start the application
streamlit run src/streamlit_app.py
```

### Production Deployment
```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Deploy to production
./scripts/deploy.sh
```

## Environment Configuration

The application automatically detects the environment:
- **Development**: macOS (Darwin) - uses local MySQL
- **Production**: Linux - uses AWS RDS

Required environment variables:
- Development: `MYSQL_USER`, `MYSQL_PWD`
- Production: `RDS_ENDPOINT`, `RDS_USER`, `RDS_PASSWORD`

## Database Schema

The application uses a MySQL database with the following table structure:

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

## Next Steps for Future Development

1. **Testing**: Expand test coverage for new service layer
2. **Data Models**: Add Pydantic models for data validation
3. **API Layer**: Consider adding REST API endpoints
4. **Caching**: Implement Redis for session caching
5. **Monitoring**: Add health checks and metrics collection