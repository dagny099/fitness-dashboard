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
    $ ~/.local/bin/poetry run python init.py


Pre-requisites:
    $ poetry install  # Within a virtual environment, install dependencies using poetry

"""

import os
import toml
import pymysql

# ----------------------------------------------
with open("pyproject.toml", "r") as f:
    config = toml.load(f)

tablename = "workout_summary"

tbl_schema = f"""
    CREATE TABLE IF NOT EXISTS {tablename} (
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
    )
    """

# 0. Create the .streamlit directory & secrets.toml file if it doesn't exist
if not(os.path.exists(".streamlit")):
    os.makedirs(".streamlit")

    # Set dummy variables for db credentials IF NOT FOUND IN THE ENVIRONMENT (for local testing)
    DB_USER = os.getenv('MYSQL_USER', 'db_user')
    DB_PASSWORD = os.getenv('MYSQL_PWD', 'db_password')

    content = f"""[connections.mysql]\ndialect = "mysql"\nhost = "localhost"\nport = 3306\ndatabase = "sweat"\nusername = "{DB_USER}"\npassword = "{DB_PASSWORD}"\n
    """
    # Create the secrets.toml file for database configuration (BE SURE TO EDIT)
    with open(".streamlit/secrets.toml", "w") as f:
        f.write(content)
        print("Created .streamlit/secrets.toml file with this info:")
        print(content)
        print("****EDIT IF NECESSARY OTHERWISE CONNECTION WILL FAIL!****")


# 1. Load database configuration (.streamlit/secrets.toml)
with open(".streamlit/secrets.toml", "r") as f:
    dbconfig = toml.load(f)
    dbconfig = dbconfig['connections']['mysql']
    print(f"\n-------\nUsing this Databse configuration:")    
    print(dbconfig)    

# 2. Establish a connection to the mysql server
connection = pymysql.connect(
        host=dbconfig["host"], port=dbconfig["port"],
        user=dbconfig["username"], password=dbconfig["password"] )

# 3. Check if 'sweat' database exists and create if not
with connection.cursor() as cursor:
    while True:    # Check what databases are available for this user
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()                 # Fetch all databases

        if any(db[0] == dbconfig['database'] for db in databases):  # Check if 'sweat' is in the list
            print(f"Database {dbconfig['database']} exists")
            break
        else:
            print(f"\nDatabase {dbconfig['database']} is not in db yet ... CREATING it now!\n")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbconfig['database']};")    

# 4. Create a new table (workout_summary) if it doesn't exist
with connection.cursor() as cursor:
    cursor.execute(f"USE {dbconfig['database']};")  # Switch to 'sweat' database
    cursor.execute(tbl_schema)  #CREATE TABLE IF NOT EXISTS
    cursor.execute(f"SELECT COUNT(*) FROM {tablename};")
    total_rows = cursor.fetchone()[0]
    print(f"Table {dbconfig['database']}.{tablename} has {total_rows} rows")    


# 5. Close the connection
cursor.close()
connection.close()
print("MySQL connection is closed")
print("-------\n")        
        
# ----------------------------------------------
#     # Get the last inserted id
#     cursor.execute("SELECT LAST_INSERT_ID()")
#     last_id = cursor.fetchone()[0]
#     print(f"The last inserted ID was: {last_id}")

