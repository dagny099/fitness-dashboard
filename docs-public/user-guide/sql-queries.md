# SQL Query Interface

The Fitness Overview section provides a powerful SQL query interface for advanced data analysis and custom reporting. This feature allows you to write custom queries to explore your fitness data in depth.

## Getting Started

### Accessing the SQL Interface

1. **Launch** the dashboard: `streamlit run src/streamlit_app.py`
2. **Navigate** to "📊 Fitness Overview" in the sidebar
3. **Find** the SQL query text area and execute button

### Basic Query Structure

The interface connects to your `workout_summary` table with the following schema:

```sql
-- Basic table structure
SELECT * FROM workout_summary LIMIT 5;
```

## Pre-built Query Examples

### Quick Start Queries

Copy and paste these queries to get started:

=== "Recent Workouts"
    
    ```sql
    SELECT 
        workout_date,
        activity_type,
        distance_mi,
        duration_sec / 60 as duration_minutes,
        kcal_burned
    FROM workout_summary 
    ORDER BY workout_date DESC 
    LIMIT 10;
    ```

=== "Monthly Summary"
    
    ```sql
    SELECT 
        DATE_FORMAT(workout_date, '%Y-%m') as month,
        COUNT(*) as total_workouts,
        ROUND(SUM(distance_mi), 2) as total_distance,
        ROUND(SUM(kcal_burned)) as total_calories,
        ROUND(AVG(duration_sec / 60), 1) as avg_duration_min
    FROM workout_summary
    GROUP BY DATE_FORMAT(workout_date, '%Y-%m')
    ORDER BY month DESC;
    ```

=== "Activity Breakdown"
    
    ```sql
    SELECT 
        activity_type,
        COUNT(*) as workout_count,
        ROUND(SUM(distance_mi), 2) as total_distance,
        ROUND(AVG(distance_mi), 2) as avg_distance,
        ROUND(SUM(kcal_burned)) as total_calories
    FROM workout_summary
    GROUP BY activity_type
    ORDER BY workout_count DESC;
    ```

### Performance Analysis Queries

=== "Personal Records"
    
    ```sql
    SELECT 
        'Longest Distance' as record_type,
        MAX(distance_mi) as value,
        workout_date,
        activity_type
    FROM workout_summary
    WHERE distance_mi = (SELECT MAX(distance_mi) FROM workout_summary)
    
    UNION ALL
    
    SELECT 
        'Most Calories',
        MAX(kcal_burned),
        workout_date,
        activity_type
    FROM workout_summary
    WHERE kcal_burned = (SELECT MAX(kcal_burned) FROM workout_summary)
    
    UNION ALL
    
    SELECT 
        'Longest Duration',
        MAX(duration_sec / 60),
        workout_date,
        activity_type
    FROM workout_summary
    WHERE duration_sec = (SELECT MAX(duration_sec) FROM workout_summary);
    ```

=== "Weekly Trends"
    
    ```sql
    SELECT 
        YEARWEEK(workout_date) as week_number,
        DATE(workout_date - INTERVAL WEEKDAY(workout_date) DAY) as week_start,
        COUNT(*) as workouts_per_week,
        ROUND(SUM(distance_mi), 2) as weekly_distance,
        ROUND(SUM(kcal_burned)) as weekly_calories,
        ROUND(AVG(duration_sec / 60), 1) as avg_workout_minutes
    FROM workout_summary
    WHERE workout_date >= DATE_SUB(NOW(), INTERVAL 12 WEEK)
    GROUP BY YEARWEEK(workout_date), week_start
    ORDER BY week_number DESC;
    ```

=== "Pace Analysis"
    
    ```sql
    SELECT 
        activity_type,
        ROUND(AVG(avg_pace), 2) as overall_avg_pace,
        ROUND(MIN(avg_pace), 2) as best_avg_pace,
        ROUND(MAX(avg_pace), 2) as slowest_pace,
        ROUND(AVG(max_pace), 2) as avg_max_pace,
        COUNT(*) as total_workouts
    FROM workout_summary
    WHERE avg_pace IS NOT NULL 
        AND avg_pace > 0
        AND activity_type IN ('Running', 'Walking')
    GROUP BY activity_type;
    ```

## Advanced Query Techniques

### Date and Time Analysis

```sql
-- Workout patterns by day of week
SELECT 
    DAYNAME(workout_date) as day_of_week,
    DAYOFWEEK(workout_date) as day_num,
    COUNT(*) as workout_count,
    ROUND(AVG(duration_sec / 60), 1) as avg_duration
FROM workout_summary
GROUP BY DAYNAME(workout_date), DAYOFWEEK(workout_date)
ORDER BY day_num;

-- Workout patterns by hour of day
SELECT 
    HOUR(workout_date) as hour_of_day,
    COUNT(*) as workout_count,
    GROUP_CONCAT(DISTINCT activity_type) as activities
FROM workout_summary
GROUP BY HOUR(workout_date)
ORDER BY hour_of_day;
```

### Comparative Analysis

```sql
-- Year-over-year comparison
SELECT 
    YEAR(workout_date) as year,
    MONTH(workout_date) as month,
    MONTHNAME(workout_date) as month_name,
    COUNT(*) as workouts,
    ROUND(SUM(distance_mi), 2) as distance,
    ROUND(SUM(kcal_burned)) as calories
FROM workout_summary
WHERE YEAR(workout_date) IN (YEAR(NOW()), YEAR(NOW())-1)
GROUP BY YEAR(workout_date), MONTH(workout_date), MONTHNAME(workout_date)
ORDER BY year DESC, month;

-- Activity comparison between time periods
SELECT 
    activity_type,
    COUNT(CASE WHEN workout_date >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as last_30_days,
    COUNT(CASE WHEN workout_date BETWEEN DATE_SUB(NOW(), INTERVAL 60 DAY) 
                                    AND DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as previous_30_days,
    ROUND(
        (COUNT(CASE WHEN workout_date >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) - 
         COUNT(CASE WHEN workout_date BETWEEN DATE_SUB(NOW(), INTERVAL 60 DAY) 
                                        AND DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END)) 
        / NULLIF(COUNT(CASE WHEN workout_date BETWEEN DATE_SUB(NOW(), INTERVAL 60 DAY) 
                                                 AND DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END), 0) * 100
    , 1) as percent_change
FROM workout_summary
WHERE workout_date >= DATE_SUB(NOW(), INTERVAL 60 DAY)
GROUP BY activity_type
HAVING last_30_days > 0 OR previous_30_days > 0
ORDER BY last_30_days DESC;
```

### Goal Tracking Queries

```sql
-- Monthly goal progress (example: 50 miles per month)
SELECT 
    DATE_FORMAT(workout_date, '%Y-%m') as month,
    ROUND(SUM(distance_mi), 2) as actual_distance,
    50 as monthly_goal,
    ROUND((SUM(distance_mi) / 50) * 100, 1) as goal_percentage,
    CASE 
        WHEN SUM(distance_mi) >= 50 THEN '✅ Goal Met'
        WHEN SUM(distance_mi) >= 40 THEN '⚠️ Close'
        ELSE '❌ Below Target'
    END as status
FROM workout_summary
WHERE workout_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
GROUP BY DATE_FORMAT(workout_date, '%Y-%m')
ORDER BY month DESC;

-- Streak analysis
SELECT 
    workout_date,
    LAG(workout_date) OVER (ORDER BY workout_date) as previous_workout,
    DATEDIFF(workout_date, LAG(workout_date) OVER (ORDER BY workout_date)) as days_between
FROM workout_summary
ORDER BY workout_date DESC
LIMIT 20;
```

## Query Optimization Tips

### Performance Best Practices

**Use Indexes Effectively**:
```sql
-- These queries use the date index efficiently
SELECT * FROM workout_summary 
WHERE workout_date >= '2024-01-01' 
AND workout_date < '2024-02-01';
```

**Limit Large Result Sets**:
```sql
-- Always use LIMIT for exploratory queries
SELECT * FROM workout_summary 
ORDER BY workout_date DESC 
LIMIT 100;
```

**Aggregate When Possible**:
```sql
-- Instead of returning all rows, aggregate first
SELECT DATE(workout_date) as workout_day, COUNT(*) as daily_count
FROM workout_summary
GROUP BY DATE(workout_date)
ORDER BY workout_day DESC;
```

### Common Query Patterns

**Rolling Averages**:
```sql
SELECT 
    workout_date,
    distance_mi,
    AVG(distance_mi) OVER (
        ORDER BY workout_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as rolling_7day_avg
FROM workout_summary
ORDER BY workout_date DESC
LIMIT 30;
```

**Percentile Analysis**:
```sql
-- Using MySQL 8.0+ window functions
SELECT 
    activity_type,
    distance_mi,
    PERCENT_RANK() OVER (PARTITION BY activity_type ORDER BY distance_mi) as percentile_rank
FROM workout_summary
WHERE activity_type = 'Running'
ORDER BY distance_mi DESC;
```

## Data Exploration Techniques

### Understanding Your Data

```sql
-- Data quality check
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT workout_id) as unique_workouts,
    MIN(workout_date) as earliest_workout,
    MAX(workout_date) as latest_workout,
    COUNT(DISTINCT activity_type) as activity_types,
    COUNT(CASE WHEN distance_mi IS NULL THEN 1 END) as missing_distance,
    COUNT(CASE WHEN kcal_burned IS NULL THEN 1 END) as missing_calories
FROM workout_summary;

-- Activity type analysis
SELECT 
    activity_type,
    COUNT(*) as frequency,
    MIN(workout_date) as first_occurrence,
    MAX(workout_date) as last_occurrence
FROM workout_summary
GROUP BY activity_type
ORDER BY frequency DESC;
```

### Finding Patterns

```sql
-- Seasonal patterns
SELECT 
    QUARTER(workout_date) as quarter,
    CASE QUARTER(workout_date)
        WHEN 1 THEN 'Q1: Jan-Mar'
        WHEN 2 THEN 'Q2: Apr-Jun'
        WHEN 3 THEN 'Q3: Jul-Sep'
        WHEN 4 THEN 'Q4: Oct-Dec'
    END as season,
    COUNT(*) as workout_count,
    ROUND(AVG(distance_mi), 2) as avg_distance,
    ROUND(AVG(kcal_burned)) as avg_calories
FROM workout_summary
GROUP BY QUARTER(workout_date)
ORDER BY quarter;
```

## Troubleshooting SQL Queries

### Common Errors

!!! error "Syntax Error"
    **Error**: `You have an error in your SQL syntax`
    
    **Common Causes**:
    - Missing quotes around string values
    - Incorrect column names (check spelling)
    - Missing commas in SELECT lists
    - Unmatched parentheses

!!! error "Unknown Column Error"
    **Error**: `Unknown column 'column_name' in 'field list'`
    
    **Solution**: Use this query to see available columns:
    ```sql
    DESCRIBE workout_summary;
    ```

!!! error "Timeout Error"
    **Error**: Query execution timeout
    
    **Solutions**:
    - Add date range filters: `WHERE workout_date >= '2024-01-01'`
    - Use LIMIT to reduce result size
    - Simplify complex JOINs and subqueries

### Performance Issues

**Slow Queries**:
- Add appropriate WHERE clauses to filter data
- Use LIMIT for large result sets
- Avoid SELECT * for large tables
- Consider using summary/aggregate queries

**Memory Issues**:
- Reduce the date range of your query
- Use streaming results for very large datasets
- Consider data archival for old records

## Advanced Features

### Custom Functions

Create reusable query patterns:

```sql
-- Distance conversion function (if needed)
SELECT 
    workout_date,
    distance_mi,
    ROUND(distance_mi * 1.609344, 2) as distance_km
FROM workout_summary
WHERE distance_mi > 0;

-- Pace formatting
SELECT 
    workout_date,
    activity_type,
    avg_pace,
    CONCAT(
        FLOOR(avg_pace), ':', 
        LPAD(ROUND((avg_pace - FLOOR(avg_pace)) * 60), 2, '0')
    ) as formatted_pace
FROM workout_summary
WHERE avg_pace IS NOT NULL AND activity_type = 'Running'
ORDER BY workout_date DESC
LIMIT 10;
```

### Export Results

The query results can be:
- **Copied** directly from the results table
- **Downloaded** as CSV using browser functionality
- **Used** as data source for custom visualizations

## Learning Resources

### SQL Learning Path

1. **Basic Queries**: Start with SELECT, WHERE, ORDER BY
2. **Aggregation**: Learn GROUP BY, COUNT, SUM, AVG
3. **Date Functions**: Master date filtering and formatting
4. **Window Functions**: Advanced analytics with OVER()
5. **Subqueries**: Complex analysis with nested queries

### Practice Exercises

Try these progressively challenging queries:

1. **Beginner**: Find your total workouts per month
2. **Intermediate**: Calculate your best pace by activity type
3. **Advanced**: Create a 30-day rolling average of daily calories

## Next Steps

Master the SQL interface to unlock powerful analytics:

1. **Save** your favorite queries for regular use
2. **Combine** SQL results with dashboard visualizations
3. **Create** custom reports for specific goals
4. **Explore** the Tools section for additional analysis features

For more advanced database topics, see the [Developer Guide](../developer/api-reference.md).