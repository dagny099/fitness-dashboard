import pandas as pd
import numpy as np
from datetime import datetime
import pymysql
import re
import toml
from typing import Dict, List, Any, Optional, Union, Tuple

from ..config.logging_config import logger

# Function to setup connectivity
def get_db_connection(dbconfig: Optional[Dict[str, Any]] = None) -> pymysql.Connection:
    connection = pymysql.connect(
            host=dbconfig["host"],
            port=dbconfig["port"],
            user=dbconfig["username"],
            password=dbconfig["password"],
            database=dbconfig["database"],
            cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def insert_data(df: pd.DataFrame, dbconfig: Optional[Dict[str, Any]] = None) -> int:
    """
    Insert dataframe rows into cursor's database table
    """

    # Get column names
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    
    # Prepare the SQL query
    sql = f"INSERT INTO workout_summary ({columns}) VALUES ({placeholders})"
    
    # Convert DataFrame to list of tuples
    data = [tuple(x) for x in df.replace({np.nan: None}).values]
    
    connection = get_db_connection(dbconfig=dbconfig)
    with connection.cursor() as cursor:
        try:
            cursor.executemany(sql, data)
            connection.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            return 0


# Function to enrich data ... More enrichment can be added here
def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich the data with additional columns
    """
    # Extract workout ID from Link
    df['workout_id'] = df['link'].apply(extract_workout_id)
    
    # TODO -- More enrichment here, e.g.
    # df['workout_year'] = pd.to_datetime(df['workout_date']).dt.year
    # df['is_long_workout'] = df['duration_sec'] > 3600

    return df

# Custom date parsing function
def parse_date(date_string: str) -> Optional[datetime]:
    """Function to parse date strings in various formats"""
    date_formats = [
        '%b. %d, %Y',  # Aug. 1, 2024
        '%d-%b-%y',    # 31-Jul-24
        '%d-%b-%Y',    # 31-Jul-2024
        '%B %d, %Y',   # July 31, 2024
        '%d-%m-%y',    # 20-06-23
        '%Y-%m-%d'     # 2024-08-01 (in case you have any in this format)
    ]   
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass    
    return None

        
# Function to clean data
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to clean data including:
        - drop unnecessary columns, 
        - drop rows with zero workout time, 
        - replace NaN values with None, 
        - date parsing for "Workout Date", and
        - rename columns to be more descriptive of units
    """

    initial_row_count = len(df)
    
    # Nix columns that I don't care about so I won't bother cleaning them
    ignore_cols = ['Date Submitted', 'Avg Speed (mi/h)', 'Max Speed (mi/h)', 'Avg Heart Rate', 'Notes','Source' ]
    df = df.drop(columns=ignore_cols)
    
    # Drop rows where 'Workout Time (seconds)' is 0
    df = df[df['Workout Time (seconds)'] != 0]
    rows_dropped = initial_row_count - len(df)   
    # print(f"Dropped {rows_dropped} rows with zero workout time.") ** ADD TO A REPORT **

    # Replace 'nan' with None for numeric columns
    numeric_columns = ['Calories Burned (kcal)', 'Distance (mi)', 'Workout Time (seconds)', 
                       'Avg Pace (min/mi)', 'Max Pace (min/mi)', 'Steps']
    for col in numeric_columns:
        df.loc[df[col].isna(), col] = None
    
    # Replace empty strings with None for string columns
    string_columns = ['Activity Type', 'Link']
    for col in string_columns:
        df.loc[df[col] == '', col] = None

    # Custom date parsing
    date_formats, invalid_dates  = {}, []   
    df['Workout Date'] = df['Workout Date'].apply(lambda x: parse_date(str(x)))
    
    for index, row in df.iterrows():
        date_string = str(row['Workout Date'])
        if isinstance(row['Workout Date'], pd._libs.tslibs.nattype.NaTType):
            invalid_dates.append((index, date_string))
        else:
            date_format = re.sub(r'\d+', '%', date_string)
            if date_format in date_formats:
                date_formats[date_format] += 1
            else:
                date_formats[date_format] = 1
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['Workout Date'])
    rows_dropped_invalid_date = len(invalid_dates)
    
    # print(f"Dropped {rows_dropped_invalid_date} rows with invalid dates.")  ** ADD TO A REPORT **
    # print(f"Final number of rows: {len(df)}") ** ADD TO A REPORT **
    
    # Replace NaN values with None
    df = df.where(pd.notnull(df), None)

    # Replace infinite values with None
    df = df.replace([np.inf, -np.inf], None)

    # Reset the index after dropping rows
    df = df.reset_index(drop=True)
    
    # Rename columns to match our database schema
    column_mapping = {
        'Workout Date': 'workout_date',
        'Activity Type': 'activity_type',
        'Calories Burned (kcal)': 'kcal_burned',
        'Distance (mi)': 'distance_mi',
        'Workout Time (seconds)': 'duration_sec',
        'Avg Pace (min/mi)': 'avg_pace',
        'Max Pace (min/mi)': 'max_pace',
        'Steps': 'steps',
        'Link': 'link'
    }
    df = df.rename(columns=column_mapping)
    
    return df


# def load_data(query="SELECT * FROM workout_summary"):
#     cursor = get_db_connection()
#     cursor.execute(query)
#     data = cursor.fetchall()  # Get all rows of the result
#     cursor.close()
#     column_names = [i[0] for i in cursor.description]  # Get column names
#     return pd.DataFrame(data, columns=column_names)  # Convert the data into a Pandas DataFrame


def execute_query(query: str, dbconfig: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Execute an arbitrary SQL query and return the results.

    Args:
        query (str): The SQL query to execute.
        query_params (tuple or dict, optional): Parameters for the query.

    Returns:
        list: List of rows as dictionaries, or an empty list if no results.
    """
    results = []

    try:
        with get_db_connection(dbconfig=dbconfig) as connection:
            with connection.cursor() as cursor:
                # Execute the query with parameters (if any)
                cursor.execute(query)
                results = cursor.fetchall()

    except pymysql.MySQLError as e:
        logger.error(f"Error executing query: {e}")

    return results



def extract_workout_id(url: str) -> str:
    match = re.search(r'/workout/(\d+)', url)
    if match:
        return match.group(1)
    else:
        return 'unsure'  # or you could return a specific value to indicate no match was found


def calculate_workout_statistics(df_sub: pd.DataFrame) -> Dict[str, Dict[str, Union[int, float]]]:
    """
    Calculate key statistics for workout data.
    
    Parameters:
    -----------
    df_sub : pandas.DataFrame
        DataFrame containing workout data with at least the following columns:
        distance_mi, duration_sec, kcal_burned, max_pace, steps
    
    Returns:
    --------
    dict
        Dictionary containing statistics for each column:
        - count: Number of non-null values
        - avg: Mean value
        - median: Median value
        - std: Standard deviation
    
    Notes:
    ------
    NaN values are handled automatically by pandas functions.
    """
    # Define columns to analyze
    columns_to_analyze = ['distance_mi', 'duration_sec', 'kcal_burned', 'max_pace', 'steps']
    
    # Initialize results dictionary
    stats = {}
    
    # Calculate statistics for each column
    for col in columns_to_analyze:
        if col in df_sub.columns:
            # Filter out missing values
            valid_data = df_sub[col].dropna()
            
            # Calculate statistics
            stats[col] = {
                'count': len(valid_data),
                'avg': valid_data.mean() if len(valid_data) > 0 else np.nan,
                'median': valid_data.median() if len(valid_data) > 0 else np.nan,
                'std': valid_data.std() if len(valid_data) > 0 else np.nan
            }
        else:
            # Handle missing columns
            stats[col] = {
                'count': 0,
                'avg': np.nan,
                'median': np.nan,
                'std': np.nan
            }
    
    return stats