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
python scripts/update_db.py
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
- **Workout Classification**: K-means clustering to automatically categorize workouts (real_run, pup_walk, mixed, outlier)
- **Era-Based Defaults**: Smart fallback classification based on Choco Effect date (pre-2018: runs, post-2018: walks)
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

## Visual Assets & Documentation Management

### Screenshot Management
The project maintains comprehensive visual assets for documentation:

```bash
# Visual assets are organized in:
docs/assets/screenshots/
├── pages/              # Full page screenshots
├── components/         # UI component screenshots
└── [legacy files]      # Older screenshots (marked for replacement)

# Use development mode + Playwright for screenshot capture:
STREAMLIT_DEV_MODE=true streamlit run src/streamlit_app.py --server.port 8501 --server.headless true &
# Then use MCP Playwright to capture screenshots
```

### Visual Assets Table of Contents
- **Location**: `docs/VISUAL_ASSETS_TOC.md` - Complete inventory of all visual assets
- **Purpose**: Reference guide for all screenshots, diagrams, and their documentation usage
- **Maintenance**: Update when adding new screenshots or UI changes

### Documentation Structure
```
docs/
├── ai/                 # AI/ML feature documentation
├── user-guide/         # End-user documentation
├── developer/          # Technical documentation
├── getting-started/    # Onboarding guides
├── reference/          # API and reference material
├── assets/             # Screenshots, diagrams, media
└── VISUAL_ASSETS_TOC.md # Visual assets inventory
```

### MkDocs Guidelines
- **Serve locally**: `mkdocs serve` for live preview
- **Build for production**: `mkdocs build`
- **Configuration**: `mkdocs.yml` defines site structure and theme
- **Extensions**: Uses Material theme with code highlighting and tabs

## AI/ML Development Guidelines

### Working with Intelligence Service
The AI system is modular and extensible:

```python
# Key AI service location: src/services/intelligence_service.py
# Add new algorithms to the ALGORITHM_REGISTRY
# Maintain algorithm transparency for all AI features
```

### Algorithm Development Workflow
1. **Implement algorithm** in appropriate service/utility file
2. **Add to algorithm registry** with transparency details
3. **Create explanation system** for user-facing descriptions
4. **Add confidence scoring** for all predictions
5. **Update algorithm transparency documentation**

### ML Model Management
- **Classification models**: K-means clustering in `intelligence_service.py`
- **Statistical models**: Trend analysis in `utils/statistics.py`
- **Consistency scoring**: Multi-dimensional analysis in `utils/consistency_analyzer.py`
- **Performance benchmarks**: <5s for 1K+ workout classification

## Git Workflow & Branch Management

### Current Branch Structure
- **Main branch**: `main` - Production-ready code
- **Feature branches**: Use descriptive names (e.g., `docs/week5-consolidation-polish`)
- **Development branches**: For ongoing feature work

### Commit Guidelines
- **Test all pages** before committing UI changes
- **Run validation scripts** for SQL documentation updates
- **Update screenshots** when UI changes affect documentation
- **Include comprehensive testing** for AI/ML feature changes

## Environment Configuration Deep Dive

### Development Environment (macOS)
```bash
# Required environment variables:
MYSQL_USER=your_mysql_user
MYSQL_PWD=your_mysql_password

# Optional for development:
STREAMLIT_DEV_MODE=true  # Bypasses authentication
```

### Production Environment (Linux)
```bash
# AWS RDS configuration:
RDS_ENDPOINT=your_rds_endpoint
RDS_USER=your_rds_user
RDS_PASSWORD=your_rds_password
```

### Testing Environment Variables
```bash
# For MCP Playwright testing:
STREAMLIT_DEV_MODE=true streamlit run src/streamlit_app.py --server.port 8501 --server.headless true
```

## Performance & Optimization Guidelines

### Caching Strategy
- **Intelligence briefs**: 10-minute cache for performance
- **Classification data**: 5-minute cache for demo features
- **Database queries**: Strategic caching in database service

### Performance Benchmarks
- **AI Classification**: <5 seconds for 1,000+ workouts
- **Intelligence Brief**: <3 seconds generation time
- **Algorithm Transparency**: <3 seconds loading time
- **Page Load**: All pages should load within 2 seconds

### Scalability Considerations
- **Database indexing**: Ensure proper indexing on workout_date and activity_type
- **Memory management**: Monitor memory usage for large datasets
- **Concurrent users**: Architecture supports 10+ concurrent users

## Troubleshooting Quick Reference

### Common Issues & Solutions

**AI Dashboard Not Loading:**
```bash
# Check AI services initialization
# Verify database connection with workout data
# Ensure ML dependencies installed (scikit-learn, scipy)
```

**Authentication Issues:**
```bash
# Use development mode bypass:
STREAMLIT_DEV_MODE=true streamlit run src/streamlit_app.py
```

**Database Connection Problems:**
```bash
# Verify environment variables are set
# Test database connection: python scripts/init.py
# Check MySQL service is running
```

**Performance Issues:**
```bash
# Check dataset size (>1K workouts may need optimization)
# Monitor memory usage and database queries
# Consider data aggregation for historical views
```

## Data Pipeline Management

### Workout Data Import
```bash
# Standard import workflow:
1. Export CSV from MapMyRun
2. Replace: src/user2632022_workout_history.csv
3. Run: python src/update_db.py
4. Verify: Check classification results in dashboard
```

### Classification System
- **real_run**: 8-12 min/mile pace, focused running
- **pup_walk**: 20-28 min/mile, walking/dog-walking activities
- **mixed**: Variable pace, combined activities
- **outlier**: Extreme values requiring attention

### Era-Based Classification Architecture

#### The Choco Effect Date
The system uses a configurable **Choco Effect Date** (default: June 1, 2018) to provide intelligent classification defaults based on behavioral patterns:

**Configuration Location:** `src/config/app.py`
```python
# Set in pyproject.toml under [tool.project.business_dates]:
choco_effect_date = "2018-06-01"
```

#### Business Logic Implementation
- **Pre-Choco Era** (before 2018-06-01): Defaults to `real_run` - running-focused period
- **Post-Choco Era** (after 2018-06-01): Defaults to `pup_walk` - walking/dog-walking period

This approach leverages years of training data patterns to provide accurate classification even when machine learning clustering has insufficient data (<5 workouts).

#### Smart Fallback Hierarchy
1. **Primary**: K-means ML clustering (requires ≥5 workouts)
2. **Secondary**: Era-based defaults (medium confidence: 0.5)
3. **Tertiary**: Rule-based classification by pace thresholds

### Data Architecture Improvements

#### Unified Data Filtering
All pages now use shared filtering utilities (`src/utils/data_filters.py`) for consistency:

- **Date Filtering**: `filter_workouts_by_date()` - supports days_lookback and explicit ranges
- **Metric Filtering**: `filter_workouts_by_metrics()` - pace, distance, duration, calories
- **Smart Suggestions**: `get_optimal_date_range_suggestion()` - recommends better timeframes

#### Eliminated Duplicate Filtering
- Intelligence Brief and View Selected Data use the same filtered dataset
- Prevents inconsistencies between "22 workouts analyzed" and "1 workout shown"
- Single source of truth for date range calculations

### Data Quality Assurance
- **Validate imports**: Check for missing fields or invalid data
- **Monitor classification confidence**: Low confidence may indicate data quality issues
- **Review outliers**: Investigate unusual patterns for data integrity
- **Era consistency**: Verify classifications align with expected pre/post-Choco patterns
- **Date consistency**: All pages use current date as reference for "days back" calculations

**Last Updated**: September 13, 2025 - Added visual assets, AI development, and comprehensive troubleshooting sections.
