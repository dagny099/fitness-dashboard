# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Fitness Dashboard is a Streamlit web application for tracking workout data with MySQL backend support. It features environment-aware configuration (Development on macOS, Production on Linux/AWS RDS) and a modular architecture with separate layers for configuration, services, views, and utilities.

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
```

### Testing
```bash
# Run tests using pytest
pytest

# Run tests with coverage
pytest --cov
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
│   └── database_service.py # Centralized database operations
├── views/              # Streamlit pages
│   ├── dash.py         # Monthly dashboard view
│   ├── fitness-overview.py # SQL query interface
│   ├── login.py        # Authentication
│   └── tools/          # Additional utilities
└── utils/              # Shared utilities
```

### Environment Configuration
- **Development** (macOS): Uses local MySQL with `MYSQL_USER` and `MYSQL_PWD` environment variables
- **Production** (Linux): Uses AWS RDS with `RDS_ENDPOINT`, `RDS_USER`, `RDS_PASSWORD` environment variables

### Database Schema
Primary table: `workout_summary` with fields for workout_id, workout_date, activity_type, kcal_burned, distance_mi, duration_sec, avg_pace, max_pace, steps, and link.

### Key Components
- **Streamlit Multi-page App**: Navigation handled in `src/streamlit_app.py`
- **Database Service**: Centralized operations in `src/services/database_service.py`
- **Authentication**: Session-based login system
- **Data Import**: CSV processing for MapMyRun workout history

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
- Supports both development and production deployment configurations
- Main application entry point is `src/streamlit_app.py`
- Database initialization must be run before first use
- Production deployment uses systemd service management