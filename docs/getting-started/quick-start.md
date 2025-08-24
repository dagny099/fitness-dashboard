# Quick Start

Get your Fitness Dashboard running in just a few minutes!

## Prerequisites

- ✅ Python 3.10+ installed
- ✅ Dependencies installed (see [Installation](installation.md))
- ✅ MySQL server running locally

## Step 1: Database Initialization

Initialize your local database with the required schema:

```bash
python scripts/init.py
```

This script will:

- Create the `sweat` database if it doesn't exist
- Set up the `workout_summary` table with the proper schema
- Configure `.streamlit/secrets.toml` with database credentials
- Verify the connection and display table status

!!! success "Database Ready"
    You should see output similar to:
    ```
    Database 'sweat' created successfully
    Table 'workout_summary' created successfully
    Current row count: 0
    ```

## Step 2: Load Sample Data (Optional)

If you have fitness data from MapMyRun:

1. Export your workout history as CSV from [MapMyRun](https://www.mapmyfitness.com/workout/export/csv)
2. Replace the sample file: `src/user2632022_workout_history.csv`
3. Update the database:

```bash
python src/update_db.py
```

## Step 3: Launch the Dashboard

Start the Streamlit application:

```bash
streamlit run src/streamlit_app.py
```

The dashboard will be available at: **http://localhost:8501**

## Step 4: Explore the Interface

Your dashboard includes several key sections:

### 🏠 Main Dashboard
- Monthly workout statistics
- Performance trends
- Activity type breakdown
- Interactive calendar view

### 📊 Fitness Overview
- SQL query interface for custom analysis
- Pre-built query examples
- Data exploration tools

### 📅 Calendar View
- Detailed workout calendar
- Daily activity summaries
- Historical data browsing

### 🔧 Tools Section
- Data import utilities
- Performance analytics
- Trend analysis

## Quick Demo

Try these features to get familiar with the dashboard:

1. **View Monthly Stats**: Check the main dashboard for your workout summary
2. **Run a Query**: Go to "Fitness Overview" and try: `SELECT * FROM workout_summary LIMIT 10`
3. **Explore Calendar**: Browse your workouts by date in the calendar view
4. **Analyze Trends**: Visit the Tools section for trend analysis

## Configuration

The application automatically detects your environment:

- **Development** (macOS): Uses local MySQL
- **Production** (Linux): Uses AWS RDS

Key configuration files:
- `.streamlit/secrets.toml` - Database credentials
- `src/config/` - Application configuration
- `.env` - Environment variables

## Sample Data Structure

Your workout data should include these key fields:

| Field | Description | Example |
|-------|-------------|---------|
| `workout_id` | Unique identifier | "12345" |
| `workout_date` | Date and time | "2024-01-15 08:30:00" |
| `activity_type` | Type of workout | "Running", "Cycling" |
| `kcal_burned` | Calories burned | 450 |
| `distance_mi` | Distance in miles | 3.2 |
| `duration_sec` | Duration in seconds | 1800 |

## Next Steps

Now that your dashboard is running:

1. **Import Your Data**: Follow the [Data Import Guide](../user-guide/data-import.md)
2. **Customize Views**: Learn about [Visualization Features](../user-guide/visualizations.md)
3. **Advanced Queries**: Master the [SQL Query Interface](../user-guide/sql-queries.md)
4. **Deploy**: Set up [Production Deployment](../deployment/production.md)

## Troubleshooting

### Dashboard Won't Load?

1. **Check the terminal** for error messages
2. **Verify database connection**: Run `python scripts/init.py` again
3. **Check port availability**: Ensure port 8501 isn't in use

### No Data Showing?

1. **Verify data import**: Check if `update_db.py` ran successfully
2. **Check database**: Run a quick query in Fitness Overview
3. **Review file path**: Ensure CSV file path in `pyproject.toml` is correct

For more help, see the [Troubleshooting Reference](../reference/troubleshooting.md) or [contact support](mailto:barbs@balex.com).