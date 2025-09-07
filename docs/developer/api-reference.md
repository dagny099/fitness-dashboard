# API Reference

This document provides detailed information about the internal APIs and functions available in the Fitness Dashboard codebase, including AI/ML services and statistical analysis utilities.

## Core Services

### DatabaseService (`src/services/database_service.py`)

The primary interface for database operations.

#### Class Definition

```python
class DatabaseService:
    """Centralized database operations with connection management and error handling"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize database service with optional configuration override"""
```

#### Connection Management

##### `get_connection()`

```python
@contextmanager
def get_connection(self) -> pymysql.Connection:
    """
    Context manager for database connections with automatic cleanup.
    
    Yields:
        pymysql.Connection: Active database connection
        
    Raises:
        DatabaseError: If connection cannot be established
        
    Example:
        with db_service.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workout_summary")
    """
```

##### `test_connection()`

```python
def test_connection(self) -> bool:
    """
    Test database connectivity.
    
    Returns:
        bool: True if connection successful, False otherwise
        
    Example:
        if not db_service.test_connection():
            logger.error("Database unavailable")
    """
```

#### Query Operations

##### `execute_query()`

```python
def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
    """
    Execute SELECT queries with optional parameters.
    
    Args:
        query (str): SQL SELECT statement
        params (Optional[Tuple]): Query parameters for prepared statements
        
    Returns:
        List[Dict]: Query results as list of dictionaries
        
    Raises:
        DatabaseError: If query execution fails
        ValidationError: If query is invalid
        
    Example:
        results = db_service.execute_query(
            "SELECT * FROM workout_summary WHERE activity_type = %s",
            ("Running",)
        )
    """
```

##### `execute_update()`

```python
def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
    """
    Execute INSERT, UPDATE, or DELETE queries.
    
    Args:
        query (str): SQL modification statement
        params (Optional[Tuple]): Query parameters
        
    Returns:
        int: Number of affected rows
        
    Raises:
        DatabaseError: If query execution fails
        
    Example:
        affected = db_service.execute_update(
            "UPDATE workout_summary SET kcal_burned = %s WHERE workout_id = %s",
            (450, "workout_123")
        )
    """
```

#### Bulk Operations

##### `bulk_insert()`

```python
def bulk_insert(self, table: str, data: List[Dict], 
                batch_size: int = 1000) -> int:
    """
    Efficiently insert multiple records.
    
    Args:
        table (str): Target table name
        data (List[Dict]): List of records to insert
        batch_size (int): Number of records per batch (default: 1000)
        
    Returns:
        int: Total number of inserted records
        
    Raises:
        DatabaseError: If bulk insert fails
        ValidationError: If data format is invalid
        
    Example:
        workouts = [
            {"workout_id": "1", "activity_type": "Running", ...},
            {"workout_id": "2", "activity_type": "Cycling", ...}
        ]
        count = db_service.bulk_insert("workout_summary", workouts)
    """
```

## AI/ML Intelligence Services

### FitnessIntelligenceService (`src/services/intelligence_service.py`)

The core AI engine providing machine learning classification and automated insights.

#### Class Definition

```python
class FitnessIntelligenceService:
    """AI-powered fitness intelligence with ML classification and analytics"""
    
    def __init__(self):
        """Initialize intelligence service with caching and ML models"""
```

#### Workout Classification

##### `classify_workout_types()`

```python
def classify_workout_types(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify workouts using K-means clustering on pace and distance patterns.
    
    Args:
        df (pd.DataFrame): Workout data with avg_pace, distance_mi columns
        
    Returns:
        pd.DataFrame: Input data enhanced with predicted_activity_type column
        
    Categories:
        - real_run: Focused running sessions (8-12 min/mile pace)
        - choco_adventure: Walking activities (20-28 min/mile pace)  
        - mixed: Sessions combining running and walking
        - outlier: Unusual patterns requiring attention
        
    Example:
        classified_df = intelligence.classify_workout_types(workout_df)
        print(classified_df['predicted_activity_type'].value_counts())
    """
```

##### `generate_daily_intelligence_brief()`

```python
def generate_daily_intelligence_brief(self, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive AI-powered fitness insights.
    
    Args:
        df (pd.DataFrame): Workout data for analysis
        
    Returns:
        Dict[str, Any]: Intelligence brief with insights, trends, and recommendations
        
    Structure:
        {
            'insights': {
                'performance': List[str],  # Performance-related insights
                'trends': List[str],       # Trend analysis insights  
                'consistency': List[str],  # Consistency observations
                'recommendations': List[str] # AI recommendations
            },
            'metrics': Dict[str, float],   # Key performance metrics
            'classification_stats': Dict   # ML model performance stats
        }
        
    Example:
        brief = intelligence.generate_daily_intelligence_brief(df)
        for insight in brief['insights']['performance']:
            print(f"💡 {insight}")
    """
```

### ConsistencyAnalyzer (`src/utils/consistency_analyzer.py`)

Multi-dimensional consistency analysis with advanced scoring algorithms.

#### Class Definition

```python
class ConsistencyAnalyzer:
    """Advanced consistency analysis and scoring system"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer with workout dataframe.
        
        Args:
            df (pd.DataFrame): Workout data with workout_date column
        """
```

#### Core Analysis Methods

##### `calculate_consistency_score()`

```python
def calculate_consistency_score(self, periods: int = 30) -> Dict[str, Any]:
    """
    Calculate comprehensive consistency score across multiple dimensions.
    
    Args:
        periods (int): Number of days to analyze for consistency
        
    Returns:
        Dict[str, Any]: Multi-dimensional consistency metrics
        
    Scoring Dimensions:
        - frequency_score: Workout frequency consistency (40% weight)
        - timing_score: Day-of-week and interval patterns (20% weight)  
        - performance_score: Metric consistency across workouts (20% weight)
        - streak_score: Current and historical streaks (20% weight)
        
    Score Range: 0-100 (higher = more consistent)
        
    Example:
        analyzer = ConsistencyAnalyzer(df)
        consistency = analyzer.calculate_consistency_score(30)
        print(f"Overall Score: {consistency['consistency_score']}")
    """
```

##### `generate_consistency_insights()`

```python
def generate_consistency_insights(self) -> List[str]:
    """
    Generate human-readable consistency insights.
    
    Returns:
        List[str]: AI-generated insights about workout consistency patterns
        
    Insight Categories:
        - Overall consistency assessment with scoring
        - Day-of-week preferences and patterns  
        - Activity type preferences and distribution
        - Frequency trends and recommendations
        
    Example:
        insights = analyzer.generate_consistency_insights()
        for insight in insights:
            print(f"🔥 {insight}")
    """
```

### Statistical Analysis Engine (`src/utils/statistics.py`)

Advanced statistical analysis with trend detection and forecasting capabilities.

#### TrendAnalysis

```python
class TrendAnalysis:
    """Advanced trend analysis for fitness metrics"""
    
    @staticmethod
    def calculate_trend(values: pd.Series, periods: int = 30) -> Dict[str, Any]:
        """
        Calculate trend analysis with statistical confidence.
        
        Returns:
            Dict containing trend_direction, trend_strength, confidence, 
            slope, r_squared, and p_value
        """
        
    @staticmethod  
    def forecast_values(values: pd.Series, periods: int = 14) -> Dict[str, Any]:
        """
        Forecast future values with confidence intervals.
        
        Returns:
            Dict with forecast arrays and confidence bounds
        """
```

#### PerformanceMetrics

```python
class PerformanceMetrics:
    """Advanced performance metrics calculation"""
    
    @staticmethod
    def calculate_consistency_score(values: pd.Series, method: str = 'cv') -> float:
        """Calculate 0-100 consistency score using coefficient of variation"""
        
    @staticmethod
    def calculate_improvement_rate(values: pd.Series, periods: int = 90) -> Dict[str, float]:
        """Calculate performance improvement rate with confidence metrics"""
```

## Configuration Management

### AppConfig (`src/config/app.py`)

Application-wide configuration management.

#### Environment Detection

```python
@staticmethod
def get_environment() -> str:
    """
    Detect current environment based on operating system.
    
    Returns:
        str: 'development' for macOS (Darwin), 'production' for Linux
        
    Example:
        env = AppConfig.get_environment()
        if env == "development":
            enable_debug_mode()
    """
```

#### Style Configuration

```python
@staticmethod
def load_style_config() -> Dict[str, Any]:
    """
    Load UI styling configuration from style_config.json.
    
    Returns:
        Dict[str, Any]: Style configuration dictionary
        
    Raises:
        ConfigurationError: If style config file cannot be loaded
        
    Example:
        styles = AppConfig.load_style_config()
        primary_color = styles["theme"]["primary_color"]
    """
```

### DatabaseConfig (`src/config/database.py`)

Database connection configuration.

#### Connection Parameters

```python
@staticmethod
def get_connection_params() -> Dict[str, Any]:
    """
    Get database connection parameters based on environment.
    
    Returns:
        Dict[str, Any]: Connection parameters including host, user, password, database
        
    Raises:
        ConfigurationError: If required environment variables are missing
        
    Example:
        params = DatabaseConfig.get_connection_params()
        connection = pymysql.connect(**params)
    """
```

## Utility Functions

### Session Management (`src/utils/session_manager.py`)

Streamlit session state management utilities.

#### SessionManager Class

```python
class SessionManager:
    """Utilities for managing Streamlit session state"""
    
    @staticmethod
    def get_session_value(key: str, default: Any = None) -> Any:
        """
        Safely retrieve value from session state.
        
        Args:
            key (str): Session state key
            default (Any): Default value if key doesn't exist
            
        Returns:
            Any: Session value or default
            
        Example:
            user_id = SessionManager.get_session_value("user_id", "anonymous")
        """
    
    @staticmethod
    def set_session_value(key: str, value: Any) -> None:
        """
        Set value in session state with validation.
        
        Args:
            key (str): Session state key
            value (Any): Value to store
            
        Example:
            SessionManager.set_session_value("current_month", "2024-01")
        """
    
    @staticmethod
    def clear_session() -> None:
        """
        Clear all session state data.
        
        Example:
            SessionManager.clear_session()  # Reset user session
        """
```

### Data Utilities (`src/utils/utilities.py`)

General utility functions with type safety.

#### Type Conversion Functions

```python
def safe_float_conversion(value: Any) -> Optional[float]:
    """
    Safely convert value to float with error handling.
    
    Args:
        value (Any): Value to convert
        
    Returns:
        Optional[float]: Converted float or None if conversion fails
        
    Example:
        distance = safe_float_conversion("3.14")  # Returns 3.14
        invalid = safe_float_conversion("abc")    # Returns None
    """

def safe_int_conversion(value: Any) -> Optional[int]:
    """
    Safely convert value to integer with error handling.
    
    Args:
        value (Any): Value to convert
        
    Returns:
        Optional[int]: Converted integer or None if conversion fails
        
    Example:
        calories = safe_int_conversion("450")  # Returns 450
        invalid = safe_int_conversion("N/A")   # Returns None
    """
```

#### Date and Time Functions

```python
def parse_workout_date(date_string: str) -> Optional[datetime]:
    """
    Parse workout date from various string formats.
    
    Args:
        date_string (str): Date string in various formats
        
    Returns:
        Optional[datetime]: Parsed datetime or None if parsing fails
        
    Supported Formats:
        - "2024-01-15 08:30:00"
        - "01/15/2024 8:30 AM"
        - "2024-01-15T08:30:00Z"
        
    Example:
        dt = parse_workout_date("2024-01-15 08:30:00")
        if dt:
            print(f"Workout was on {dt.date()}")
    """

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds (int): Duration in seconds
        
    Returns:
        str: Formatted duration string
        
    Example:
        duration = format_duration(3665)  # Returns "1h 1m 5s"
        duration = format_duration(90)    # Returns "1m 30s"
    """
```

#### Performance Calculations

```python
def calculate_pace(distance_mi: float, duration_sec: int) -> Optional[float]:
    """
    Calculate pace in minutes per mile.
    
    Args:
        distance_mi (float): Distance in miles
        duration_sec (int): Duration in seconds
        
    Returns:
        Optional[float]: Pace in minutes per mile, or None if invalid input
        
    Example:
        pace = calculate_pace(3.1, 1860)  # Returns 10.0 (10 min/mile)
    """

def calculate_speed_mph(distance_mi: float, duration_sec: int) -> Optional[float]:
    """
    Calculate speed in miles per hour.
    
    Args:
        distance_mi (float): Distance in miles
        duration_sec (int): Duration in seconds
        
    Returns:
        Optional[float]: Speed in MPH, or None if invalid input
        
    Example:
        speed = calculate_speed_mph(6.0, 3600)  # Returns 6.0 MPH
    """
```

## Data Models

### Workout Data Structure

The core workout data follows this schema:

```python
from typing import Optional, Dict, Any
from datetime import datetime

class WorkoutData:
    """
    Represents a single workout record.
    
    Attributes:
        workout_id (str): Unique workout identifier
        workout_date (datetime): When the workout occurred  
        activity_type (str): Type of activity (Running, Cycling, etc.)
        kcal_burned (Optional[int]): Calories burned
        distance_mi (Optional[float]): Distance in miles
        duration_sec (Optional[int]): Duration in seconds
        avg_pace (Optional[float]): Average pace in min/mile
        max_pace (Optional[float]): Best pace in min/mile
        steps (Optional[int]): Step count
        link (Optional[str]): Link to original workout data
    """
    
    def __init__(self, **kwargs):
        self.workout_id: str = kwargs["workout_id"]
        self.workout_date: datetime = kwargs["workout_date"]
        self.activity_type: str = kwargs["activity_type"]
        self.kcal_burned: Optional[int] = kwargs.get("kcal_burned")
        self.distance_mi: Optional[float] = kwargs.get("distance_mi")
        self.duration_sec: Optional[int] = kwargs.get("duration_sec")
        self.avg_pace: Optional[float] = kwargs.get("avg_pace")
        self.max_pace: Optional[float] = kwargs.get("max_pace")
        self.steps: Optional[int] = kwargs.get("steps")
        self.link: Optional[str] = kwargs.get("link")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workout to dictionary format for database insertion."""
        return {
            "workout_id": self.workout_id,
            "workout_date": self.workout_date,
            "activity_type": self.activity_type,
            "kcal_burned": self.kcal_burned,
            "distance_mi": self.distance_mi,
            "duration_sec": self.duration_sec,
            "avg_pace": self.avg_pace,
            "max_pace": self.max_pace,
            "steps": self.steps,
            "link": self.link
        }
    
    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'WorkoutData':
        """Create WorkoutData from CSV row with data validation."""
        return cls(
            workout_id=row["Workout Id"],
            workout_date=parse_workout_date(row["Workout Date"]),
            activity_type=row["Activity Type"],
            kcal_burned=safe_int_conversion(row.get("Total Calories")),
            distance_mi=safe_float_conversion(row.get("Distance (mi)")),
            duration_sec=safe_int_conversion(row.get("Duration")),
            avg_pace=safe_float_conversion(row.get("Avg Pace (min/mi)")),
            max_pace=safe_float_conversion(row.get("Max Pace (min/mi)")),
            steps=safe_int_conversion(row.get("Steps")),
            link=row.get("Reference")
        )
```

## Error Handling

### Exception Classes

```python
class FitnessAppError(Exception):
    """Base exception class for fitness application errors."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.details = details or {}
        
class DatabaseError(FitnessAppError):
    """Raised when database operations fail."""
    pass
    
class ValidationError(FitnessAppError):
    """Raised when data validation fails."""
    pass
    
class ConfigurationError(FitnessAppError):
    """Raised when configuration is invalid or missing."""
    pass
```

### Error Handling Patterns

```python
def safe_database_operation(operation_func: Callable) -> Any:
    """
    Wrapper for database operations with standardized error handling.
    
    Args:
        operation_func: Function to execute safely
        
    Returns:
        Any: Operation result or None if failed
        
    Example:
        result = safe_database_operation(
            lambda: db_service.execute_query("SELECT COUNT(*) FROM workout_summary")
        )
    """
    try:
        return operation_func()
    except pymysql.Error as e:
        logger.error(f"Database error: {e}")
        raise DatabaseError(f"Database operation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise FitnessAppError(f"Operation failed: {str(e)}")
```

## Logging and Monitoring

### Logging Configuration

```python
import logging
from src.config.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Usage examples
logger.info("Database connection established")
logger.warning("No workouts found for specified date range")
logger.error("Failed to process CSV file", exc_info=True)
```

### Performance Monitoring

```python
from functools import wraps
import time

def monitor_performance(func):
    """
    Decorator for monitoring function execution time.
    
    Example:
        @monitor_performance
        def expensive_query():
            return db_service.execute_query("SELECT * FROM large_table")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper
```

## Testing Utilities

### Test Fixtures

```python
import pytest
from src.services.database_service import DatabaseService

@pytest.fixture
def mock_database_service():
    """Mock database service for testing."""
    class MockDatabaseService:
        def execute_query(self, query: str, params=None):
            # Return mock data based on query
            return [{"workout_id": "test1", "activity_type": "Running"}]
    
    return MockDatabaseService()

@pytest.fixture
def sample_workout_data():
    """Sample workout data for testing."""
    return {
        "workout_id": "test123",
        "workout_date": datetime(2024, 1, 15, 8, 30),
        "activity_type": "Running",
        "kcal_burned": 450,
        "distance_mi": 3.1,
        "duration_sec": 1860,
        "avg_pace": 10.0,
        "max_pace": 8.5,
        "steps": 4200,
        "link": "https://example.com/workout/test123"
    }
```

## Extension Points

### Custom Data Sources

To add support for new fitness platforms:

```python
class CustomDataImporter:
    """Base class for implementing custom data importers."""
    
    def parse_csv(self, file_path: str) -> List[WorkoutData]:
        """Parse CSV file and return WorkoutData objects."""
        raise NotImplementedError
    
    def validate_data(self, workouts: List[WorkoutData]) -> List[WorkoutData]:
        """Validate and clean workout data."""
        raise NotImplementedError
    
    def import_data(self, file_path: str) -> int:
        """Complete import process."""
        workouts = self.parse_csv(file_path)
        validated_workouts = self.validate_data(workouts)
        return self.bulk_insert_workouts(validated_workouts)

# Example implementation for Strava
class StravaImporter(CustomDataImporter):
    def parse_csv(self, file_path: str) -> List[WorkoutData]:
        # Strava-specific parsing logic
        pass
```

### Custom Visualizations

To add new visualization types:

```python
def create_custom_chart(data: List[Dict], chart_type: str) -> Any:
    """
    Create custom Plotly charts based on data and type.
    
    Args:
        data: Chart data
        chart_type: Type of chart to create
        
    Returns:
        Plotly figure object
    """
    if chart_type == "heatmap":
        return create_activity_heatmap(data)
    elif chart_type == "performance_trend":
        return create_performance_trend_chart(data)
    else:
        raise ValueError(f"Unknown chart type: {chart_type}")
```

For more implementation examples, see the [Contributing Guide](contributing.md).