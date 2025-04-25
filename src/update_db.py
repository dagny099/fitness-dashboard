"""
update_db.py

Usage:
    Run this script from main directory to update the database with new workout data from a CSV file.
    $ ~/.local/bin/poetry run python build_workout_dashboard/update_db.py

    Nothing is added if CSV file already is consistent with the database.

Pre-requisites:
    $ ~/.local/bin/poetry run python init.py     # Initialize the database
"""

from utilities import execute_query, insert_data, clean_data, enrich_data
import os
import toml
import pandas as pd
import toml

# ----------------------------------------------
# Get the project & database configuration
with open("pyproject.toml", "r") as f:
    config = toml.load(f)

# Get the input file path: for `user2632022_workout_history.csv`
input_filepath = 'build_workout_dashboard' + os.path.sep + config['tool']['project']['input_filename'] 

# Load the CSV file with full workout history
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
with open(".streamlit/secrets.toml", "r") as f:
    dbconfig = toml.load(f)
    dbconfig = dbconfig['connections']['mysql']
    print(f"\nUsing this Databse configuration:")    
    print(dbconfig)    


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
