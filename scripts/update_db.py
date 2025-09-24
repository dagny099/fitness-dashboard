"""
update_db.py

Usage:
    Run this script from main directory to update the database with new workout data from a CSV file.
    $ ~/.local/bin/poetry run python build_workout_dashboard/update_db.py

    Nothing is added if CSV file already is consistent with the database.

Pre-requisites:
    $ ~/.local/bin/poetry run python init.py     # Initialize the database
"""
import sys
import os
# Add project root to Python path -- This lets the "src" folder to be found below
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.utilities import execute_query, insert_data, clean_data, enrich_data
import os
import toml
import platform

# ----------------------------------------------
# Get the project & database configuration
with open("pyproject.toml", "r") as f:
    config = toml.load(f)

# Get the input file path: for `user2632022_workout_history.csv`
input_filepath = 'src' + os.path.sep + config['tool']['project']['input_filename'] 

# Load the CSV file with full workout history
import pandas as pd
if os.path.exists(input_filepath):
    print(f'\n-------\nChecking for workout data in this file: {input_filepath}')
    df = pd.read_csv(input_filepath)
else:
    print(f"File {input_filepath} not found. Please check the path in pyproject.toml")
    exit(1)

# Prepare data for import into database
df = clean_data(df)         

# Enrich data (for now, just extract workoutID)
df = enrich_data(df)        

print(f"Workout CSV has {df.shape[0]} entries (includes entries probably already in db)")

tablename = "workout_summary"

# ----------------------------------------------
# DATABASE INTERACTIONS START HERE

# 1. Load database configuration (.streamlit/secrets.toml)
if platform.system() == "Darwin":
    ENV = "development"
    connection_type = "Local"
else:
    ENV = "production"
    connection_type = "Remote"

# Load db config from .streamlit/secrets.toml
if connection_type == "Local":
    dbconfig = {
        "host": "localhost",  # or your local DB host
        "port": 3306,         # default MySQL port
        "username": os.environ.get("MYSQL_USER"),
        "password": os.environ.get("MYSQL_PWD")
}
else:
    dbconfig = {
        "host": os.getenv("RDS_ENDPOINT"),
        "port": 3306,
        "username": os.getenv("RDS_USER"),
        "password": os.getenv("RDS_PASSWORD")
    }
dbconfig['database'] = "sweat"  # Database name

# 2. Query database for existing workouts
query = "SELECT workout_id FROM workout_summary"
response = execute_query(query, dbconfig)  # Check what databases are available for this user

# 3. Insert any new workouts into the table
if len(response) == 0:
    print("No existing workouts in the table")


# Use the pk (workout_id) to exclude 
workout_ids = [row['workout_id'] for row in response]
newDf = df[~df['workout_id'].isin(workout_ids)]  

# INSERT NEW WORKOUTS IN TABLE
rows_affected = insert_data(newDf, dbconfig)

print(f"\nExisting workouts in table: {len(workout_ids)} | New workouts to import: {newDf.shape[0]}")
print(f"\nInserted {rows_affected} rows into {tablename}")
