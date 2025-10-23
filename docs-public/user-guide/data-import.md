# Data Import

Learn how to import your fitness data from various sources into the Fitness Dashboard.

## Supported Data Sources

The dashboard is currently optimized for **MapMyRun** data but can be adapted for other fitness platforms with CSV export capabilities.

### MapMyRun (Recommended)

MapMyRun provides comprehensive workout data that integrates seamlessly with the dashboard.

#### Exporting from MapMyRun

1. **Sign in** to your MapMyRun account
2. **Navigate** to [MapMyRun Export](https://www.mapmyfitness.com/workout/export/csv)
3. **Select date range** for your export (or choose "All Time")
4. **Download** the CSV file

#### Expected Data Format

Your MapMyRun export should include these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `Workout Id` | Unique identifier | "2632022148" |
| `Workout Date` | Date and time | "2024-01-15 08:30:00" |
| `Activity Type` | Exercise category | "Running", "Cycling" |
| `Total Calories` | Energy burned | "450" |
| `Distance (mi)` | Miles covered | "3.2" |
| `Duration` | Time in seconds | "1800" |
| `Avg Pace (min/mi)` | Average pace | "8.5" |
| `Max Pace (min/mi)` | Best pace | "7.2" |
| `Steps` | Step count | "4200" |
| `Reference` | Link to workout | "https://..." |

### Other Fitness Platforms

The dashboard can be adapted for other platforms with similar data structures:

- **Strava**: Export GPX/CSV data
- **Garmin Connect**: CSV export from activity history
- **Fitbit**: Data export via Fitbit API
- **Apple Health**: Health app data export
- **Google Fit**: Takeout data export

## Import Process

### Step 1: Prepare Your Data File

1. **Download** your fitness data as CSV
2. **Save** the file in the `src/` directory of your project
3. **Note** the exact filename for configuration

### Step 2: Configure Data Source

Update your `pyproject.toml` file to reference your data file:

```toml
[tool.project]
input_filename = "your_workout_history.csv"
debug = true
```

### Step 3: Run Import Script

Execute the data import process:

```bash
cd /path/to/fitness-dashboard
python scripts/update_db.py
```

!!! note "Linux or Windows"
    Export `FITNESS_DASHBOARD_ENV=development` before running imports to keep the connection pointed at your local MySQL instance. Otherwise set the `RDS_*` credentials for your remote database.

The script will:

- ✅ Read your CSV file
- ✅ Validate data format and structure
- ✅ Clean and normalize data
- ✅ Insert records into the database
- ✅ Report import statistics

### Step 4: Verify Import

Check that your data was imported successfully:

1. **Launch** the dashboard: `streamlit run src/streamlit_app.py`
2. **Navigate** to Fitness Overview
3. **Run query**: `SELECT COUNT(*) FROM workout_summary;`
4. **Check** the main dashboard for your workout data

## Data Mapping and Transformation

### Column Mapping

The import process maps CSV columns to database fields:

```python
# Example mapping (in update_db.py)
column_mapping = {
    'Workout Id': 'workout_id',
    'Workout Date': 'workout_date', 
    'Activity Type': 'activity_type',
    'Total Calories': 'kcal_burned',
    'Distance (mi)': 'distance_mi',
    'Duration': 'duration_sec',
    'Avg Pace (min/mi)': 'avg_pace',
    'Max Pace (min/mi)': 'max_pace',
    'Steps': 'steps',
    'Reference': 'link'
}
```

### Data Cleaning

The import process includes automatic data cleaning:

- **Date Parsing**: Converts various date formats to MySQL DATETIME
- **Numeric Validation**: Ensures numeric fields contain valid numbers
- **Text Normalization**: Standardizes activity type names
- **Duplicate Detection**: Prevents importing duplicate workouts
- **Missing Data Handling**: Sets appropriate defaults for missing fields

## Custom Data Sources

### Adapting for New Platforms

To support a new fitness platform:

1. **Analyze** the CSV structure from your platform
2. **Update** column mapping in `src/update_db.py`
3. **Modify** data transformation logic if needed
4. **Test** with a small data sample

### Manual Data Entry

For manual data entry or custom tracking:

Create a CSV file with the required columns:

```csv
workout_id,workout_date,activity_type,kcal_burned,distance_mi,duration_sec,avg_pace,max_pace,steps,link
manual_001,2024-01-15 08:00:00,Running,300,2.5,1200,8.0,7.5,3000,
manual_002,2024-01-16 09:00:00,Cycling,400,10.0,2400,,,5000,
```

## Batch Import Operations

### Large Dataset Handling

For large datasets (1000+ workouts):

1. **Split** large CSV files into smaller batches
2. **Import** progressively to monitor progress
3. **Use** database transactions for data integrity
4. **Monitor** memory usage during import

```bash
# Example: Split large file
head -n 1 large_file.csv > header.csv
tail -n +2 large_file.csv | split -l 500 - batch_
for file in batch_*; do
    cat header.csv $file > import_$file.csv
done
```

### Incremental Updates

For regular data updates:

1. **Export** only new workouts since last import
2. **Use** date-based filtering in your export
3. **Run** import script regularly (weekly/monthly)
4. **Verify** no duplicate records are created

## Data Quality and Validation

### Pre-Import Validation

Before importing, validate your data:

```python
import pandas as pd

# Load and inspect data
df = pd.read_csv('your_data.csv')
print(f"Records: {len(df)}")
print(f"Date range: {df['Workout Date'].min()} to {df['Workout Date'].max()}")
print(f"Activities: {df['Activity Type'].unique()}")
print(f"Missing values: {df.isnull().sum()}")
```

### Post-Import Verification

After import, verify data quality:

```sql
-- Check record count
SELECT COUNT(*) as total_workouts FROM workout_summary;

-- Check date range
SELECT MIN(workout_date) as earliest, MAX(workout_date) as latest 
FROM workout_summary;

-- Check activity distribution  
SELECT activity_type, COUNT(*) as count 
FROM workout_summary 
GROUP BY activity_type 
ORDER BY count DESC;

-- Check for anomalies
SELECT * FROM workout_summary 
WHERE distance_mi > 50 OR duration_sec > 14400; -- Potential data errors
```

## Troubleshooting Import Issues

### Common Problems

!!! error "File Not Found"
    **Error**: `FileNotFoundError: No such file or directory`
    
    **Solution**: 
    - Verify file path in `pyproject.toml`
    - Ensure CSV file is in the correct directory
    - Check file permissions

!!! error "CSV Format Error"
    **Error**: `pandas.errors.EmptyDataError` or parsing errors
    
    **Solutions**:
    - Check CSV file encoding (UTF-8 recommended)
    - Verify column headers match expected format
    - Remove or escape special characters in data

!!! error "Database Connection Error"
    **Error**: `pymysql.err.OperationalError`
    
    **Solutions**:
    - Verify database is running
    - Check credentials in `.env` file
    - Ensure database and table exist

!!! error "Duplicate Key Error"
    **Error**: `pymysql.err.IntegrityError: Duplicate entry`
    
    **Solutions**:
    - Check for duplicate workout IDs in CSV
    - Clear existing data if re-importing: `DELETE FROM workout_summary;`
    - Implement upsert logic for updates

### Data Quality Issues

!!! warning "Missing Data"
    **Symptoms**: Empty fields or null values in dashboard
    
    **Solutions**:
    - Review CSV file for completeness
    - Update import script to handle missing values
    - Set appropriate defaults for optional fields

!!! warning "Incorrect Dates"
    **Symptoms**: Workouts appearing in wrong time periods
    
    **Solutions**:
    - Verify date format in CSV matches parser expectations
    - Check timezone handling in import script
    - Manually inspect problematic date entries

## Advanced Import Features

### Automated Imports

Set up automated data imports:

```bash
#!/bin/bash
# auto_import.sh - Automated import script

# Download latest data (platform-specific)
# ... download logic ...

# Run import
cd /path/to/fitness-dashboard
python scripts/update_db.py

# Log results
echo "Import completed: $(date)" >> import.log
```

Schedule with cron:

```bash
# Run weekly on Sunday at 2 AM
0 2 * * 0 /path/to/auto_import.sh
```

### API Integration

For real-time data integration (future enhancement):

```python
# Example: Strava API integration
import requests

def fetch_strava_activities(access_token):
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()
```

## Next Steps

After successfully importing your data:

1. **Explore Visualizations**: Learn about [Visualization Features](visualizations.md)
2. **Run Custom Analysis**: Use the [SQL Query Interface](sql-queries.md)
3. **Set Up Regular Updates**: Establish a routine import schedule
4. **Monitor Data Quality**: Regularly validate imported data

For additional help, see the [Troubleshooting Reference](../reference/troubleshooting.md).