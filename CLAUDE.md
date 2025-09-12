# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Fitness Dashboard is an AI-powered Streamlit web application for intelligent workout tracking and analysis. Built with MySQL backend support and featuring machine learning classification, statistical analysis, and automated insight generation. It includes environment-aware configuration (Development on macOS, Production on Linux/AWS RDS) and a modular architecture with separate layers for configuration, services, views, and utilities.

## Development Commands

### Database Setup
```bash
# Initialize database and create tables
python scripts/init.py

# Update database with workout data
python src/update_db.py
```

### Running the Application
```bash
# Start the Streamlit dashboard
streamlit run src/streamlit_app.py

# Start with development mode (bypasses login for testing)
STREAMLIT_DEV_MODE=true streamlit run src/streamlit_app.py
```

### Testing
```bash
# Run tests using pytest
pytest

# Run tests with coverage
pytest --cov

# Start app in development mode for Playwright/MCP testing
STREAMLIT_DEV_MODE=true streamlit run src/streamlit_app.py --server.port 8501 --server.headless true
```

### Documentation
```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

### Deployment
```bash
# Deploy to production (requires server access)
./scripts/deploy.sh
```

## Architecture

### Project Structure
```
src/
├── config/              # Environment-aware configuration
│   ├── database.py      # Database connection settings
│   ├── app.py          # Application configuration
│   └── logging_config.py # Logging setup
├── services/           # Business logic layer
│   ├── database_service.py # Centralized database operations
│   └── intelligence_service.py # AI/ML intelligence engine
├── utils/              # Analytics and AI utilities
│   ├── statistics.py   # Statistical analysis engine
│   └── consistency_analyzer.py # Multi-dimensional consistency scoring
├── views/              # Streamlit pages
│   ├── dash.py         # Monthly dashboard view
│   ├── choco_effect.py # AI-powered portfolio dashboard
│   ├── fitness-overview.py # SQL query interface
│   ├── login.py        # Authentication
│   └── tools/          # Analysis tools
│       ├── trends.py   # Statistical trend analysis
│       ├── history.py  # Workout history with AI insights
│       └── mapping.py  # Geographic visualization
└── scripts/            # Database initialization
    └── init.py         # Database setup script
```

### Environment Configuration
- **Development** (macOS): Uses local MySQL with `MYSQL_USER` and `MYSQL_PWD` environment variables
- **Production** (Linux): Uses AWS RDS with `RDS_ENDPOINT`, `RDS_USER`, `RDS_PASSWORD` environment variables

### Database Schema
Primary table: `workout_summary` with fields for workout_id, workout_date, activity_type, kcal_burned, distance_mi, duration_sec, avg_pace, max_pace, steps, and link.

### Key Components
- **Streamlit Multi-page App**: Navigation handled in `src/streamlit_app.py`
- **Database Service**: Centralized operations in `src/services/database_service.py`
- **AI Intelligence Engine**: ML classification and analytics in `src/services/intelligence_service.py`
- **Statistical Analysis**: Advanced analytics in `src/utils/statistics.py` and `src/utils/consistency_analyzer.py`
- **Authentication**: Session-based login system with development mode bypass
- **Data Import**: CSV processing for MapMyRun workout history

### AI/ML Features
- **Workout Classification**: K-means clustering to automatically categorize workouts (real_run, choco_adventure, mixed, outlier)
- **Trend Analysis**: Statistical trend detection with confidence intervals and forecasting
- **Anomaly Detection**: Outlier identification using IQR, z-score, and modified z-score methods  
- **Consistency Scoring**: Multi-dimensional analysis of frequency, timing, performance, and streak patterns
- **Intelligence Briefing**: Automated generation of personalized workout insights and recommendations

## Development Setup

### Option A: Virtual Environment
```bash
python3 -m venv .st-db
source .st-db/bin/activate
poetry install
```

### Option B: Direnv (Recommended)
```bash
poetry config virtualenvs.in-project true
poetry install
# Setup .envrc with auto-activation
direnv allow
```

## Important Notes

- Uses Poetry for dependency management with `package-mode = false`
- **Dependencies**: Includes scipy, scikit-learn for ML features; plotly for interactive visualizations
- Supports both development and production deployment configurations  
- Main application entry point is `src/streamlit_app.py`
- Database initialization must be run before first use (`python scripts/init.py`)
- Production deployment uses systemd service management
- **AI Features**: Fitness intelligence system provides automated workout classification and personalized insights
- **The Choco Effect**: Specialized portfolio dashboard showcasing behavioral transformation through data analysis

## SQL Documentation Guidelines

**CRITICAL: Always validate SQL examples before committing documentation changes.**

### SQL Query Validation Requirements

1. **Test All Queries**: Every SQL example in documentation must be tested against the actual database
2. **Run Validation Script**: Use `python scripts/validate_sql_docs.py` before committing documentation
3. **MySQL Compatibility**: Ensure queries work with the current MySQL version (9.2.0) and `sql_mode=only_full_group_by`

### Common SQL Issues to Avoid

1. **Reserved Word Aliases**: 
   - ❌ `SELECT NOW() as current_time` 
   - ✅ `SELECT NOW() as 'current_time'` or `SELECT NOW() as execution_time`

2. **GROUP BY Compliance**:
   - ❌ `SELECT col1, COUNT(*) FROM table GROUP BY col2` (missing col1 in GROUP BY)
   - ✅ `SELECT col1, COUNT(*) FROM table GROUP BY col1, col2`

3. **Aggregation Without GROUP BY**:
   - ❌ `SELECT MAX(col1), col2 FROM table` (non-aggregated col2)
   - ✅ `SELECT col1, col2 FROM table WHERE col1 = (SELECT MAX(col1) FROM table)`

### Prevention Strategy

- **Before adding SQL examples**: Test each query in the actual Streamlit SQL interface
- **For multi-statement blocks**: Test each statement separately
- **Reserved words to watch**: `current_time`, `current_date`, `date`, `time`, `order`, `group`, `user`
- **Always quote problematic aliases**: Use single quotes or backticks for column aliases that might be reserved
- **Regular validation**: Run the validation script as part of documentation updates

## Development Mode & Testing

### Development Mode Bypass
For testing and development, the application includes a login bypass feature that skips the authentication screen:

**Environment Variable Method:**
```bash
STREAMLIT_DEV_MODE=true streamlit run src/streamlit_app.py
```

**URL Parameter Method:**
```bash
# Start normally, then navigate to:
http://localhost:8501/?dev_mode=true
```

### Benefits for Testing
- **Direct Page Access**: Navigate directly to any page URL without login
- **MCP Playwright Integration**: Test individual pages without authentication barriers
- **Automated Testing**: Enable CI/CD testing workflows
- **Development Workflow**: Skip login during development iterations

### Usage Guidelines
- **Development Only**: Never use in production environments
- **Testing Automation**: Essential for Playwright/browser automation testing
- **Page-Specific Testing**: Test individual Streamlit pages directly via URL
- **Debugging**: Access any page instantly for debugging session state issues

### MCP Playwright Testing
When using MCP Playwright tools for testing:
1. Start app with `STREAMLIT_DEV_MODE=true` 
2. Navigate directly to specific pages (e.g., `http://localhost:8501/dash`)
3. Test interactive elements without authentication barriers
4. Capture screenshots and analyze page functionality

## Debugging and Error Handling Best Practices

### Common Error Patterns and Solutions

Based on comprehensive testing and bug fixing, these are common issues and defensive programming patterns to follow:

#### 1. Type Conversion Issues
**Problem**: Functions receiving string parameters when expecting integers
```python
# ❌ Problematic - will fail if week_num is string
start_date = datetime(year, month, month_calendar[week_num-1][0])

# ✅ Defensive - handles both string and int inputs
if isinstance(week_num, str):
    try:
        week_num = int(week_num)
    except ValueError:
        week_num = 1  # Safe fallback
```

#### 2. Null/None Value Handling
**Problem**: Processing None values without checks
```python
# ❌ Problematic - will fail if selected_year is None
detail_selected_year = int(selected_year)

# ✅ Defensive - handles None with fallback
if selected_year is None:
    detail_selected_year = datetime.now().year
else:
    detail_selected_year = int(selected_year)
```

#### 3. Database Column Existence
**Problem**: Accessing DataFrame columns that may not exist
```python
# ❌ Problematic - will fail if column missing
avg_distance = round(df['distance_mi'].mean(), 2)

# ✅ Defensive - checks column existence with fallback
avg_distance = round(df['distance_mi'].mean(), 2) if 'distance_mi' in df.columns and not df.empty else 0
```

#### 4. Data Structure Type Checking  
**Problem**: Inconsistent return types from services
```python
# ❌ Problematic - assumes consistent data structure
consistency_score = consistency_score_data['consistency_score']

# ✅ Defensive - handles both dict and scalar returns
if isinstance(consistency_score_data, dict):
    consistency_score = consistency_score_data.get('consistency_score', 0)
else:
    consistency_score = consistency_score_data
```

#### 5. Division by Zero Prevention
**Problem**: Mathematical operations without zero checks
```python
# ❌ Problematic - will fail if denominator is zero
transformation_factor = post_choco_freq / pre_choco_freq

# ✅ Defensive - handles zero with meaningful fallback
if pre_choco_freq == 0:
    transformation_text = "∞x increase - started from zero!" if post_choco_freq > 0 else "No data available"
else:
    transformation_factor = post_choco_freq / pre_choco_freq
```

### Testing with Real Data

**Best Practice**: Always test with actual workout data, not empty databases
```bash
# Add test data to database
python scripts/init.py
python src/update_db.py

# Test with development mode
STREAMLIT_DEV_MODE=true streamlit run src/streamlit_app.py --server.port 8501 --server.headless true
```

### Comprehensive Page Testing Approach

1. **Start with authentication bypass**: `STREAMLIT_DEV_MODE=true`
2. **Test each major page systematically**:
   - `/` (AI Intelligence)
   - `/dash` (Dashboard)
   - `/choco_effect` (Choco Effect)
   - `/fitness-overview` (SQL Query)
   - `/calendar_more` (Calendar)
   - `/trends` (Trends Analysis)
3. **Verify interactive elements work**: dropdowns, buttons, charts
4. **Check for error messages**: Look for red error boxes
5. **Test with edge cases**: empty data, missing columns, None values

### MCP Playwright Integration

For automated browser testing:
```bash
# Start app in background with dev mode
STREAMLIT_DEV_MODE=true streamlit run src/streamlit_app.py --server.port 8501 --server.headless true &

# Test pages directly without authentication
# Navigate to: http://localhost:8501/[page_name]
# Take screenshots to verify functionality
```

**Status**: All 6 major pages have been tested and verified working with comprehensive real data as of September 2025.