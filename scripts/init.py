"""
init.py

This script sets up the environment for this Streamlit application by performing the following tasks:

1. Creates a '.streamlit' directory in the current working directory, if none exists.
2. Populates the '.streamlit' directory with a 'secrets.toml' file, if none exists.
3. Initializes a data source:
    - Creates a new MYSQL database (sweat) if it doesn't exist
    - Establishes a connection to the database.
    - Creates a new table (workout_summary) if it doesn't exist 

Usage:
    Run this script from main project directory to prepare the environment and initialize the database:
    $ ~/.local/bin/poetry run python scripts/init.py


Pre-requisites:
    $ poetry install  # Within a virtual environment, install dependencies using poetry

"""
import sys
import os
# Add project root to Python path -- This lets the "src" folder to be found below
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import toml
import pymysql
import platform
import logging
from src.config.database import DatabaseConfig
from src.services.database_service import DatabaseService

# ----------------------------------------------
# with open("pyproject.toml", "r") as f:
#     config = toml.load(f)

tablename = "workout_summary"

# Initialize database service
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Initializing database service...")
db_config = DatabaseConfig.from_environment()
db_service = DatabaseService(db_config)

env = "DEVELOPMENT" if platform.system() == "Darwin" else "PRODUCTION"
logger.info(f"Running in {env} mode")

# Test database connection
if db_service.test_connection():
    logger.info("✅ Database connection successful")
else:
    logger.error("❌ Database connection failed")
    exit(1)

# Create database if it doesn't exist
logger.info("Checking/creating database...")
db_service.create_database_if_not_exists()

# Create tables if they don't exist
logger.info("Creating tables if they don't exist...")
db_service.create_tables_if_not_exist()

# Get table information
table_info = db_service.get_table_info(tablename)
logger.info(f"Table {table_info['table_name']} has {table_info['row_count']} rows")
if table_info['last_workout_date']:
    logger.info(f"Last workout date: {table_info['last_workout_date']}")
else:
    logger.info("No workouts found in database")

logger.info("Database initialization completed successfully!")
logger.info("-------")

# Old implementation (replaced with service-based approach)
# 4. Create a new table (workout_summary) if it doesn't exist
# Old code removed - using service-based approach above

