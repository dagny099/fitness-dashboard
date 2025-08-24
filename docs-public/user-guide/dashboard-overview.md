# Dashboard Overview

The Fitness Dashboard provides an intuitive interface for tracking and analyzing your workout data. This guide covers the main features and navigation.

## Main Interface

When you first launch the dashboard at `http://localhost:8501`, you'll see the main interface with several key sections accessible via the sidebar navigation.

### Navigation Menu

The sidebar contains the following sections:

- **🏠 Dashboard**: Monthly overview and key statistics
- **📊 Fitness Overview**: SQL query interface for advanced analysis  
- **📅 Calendar**: Calendar view of your workouts
- **🔧 Tools**: Additional analysis tools and utilities

## Dashboard Home

The main dashboard provides a comprehensive monthly view of your fitness activities.

### Key Metrics

The top of the dashboard displays important summary statistics:

- **Total Workouts**: Number of completed workouts this month
- **Total Distance**: Cumulative distance covered
- **Total Calories**: Calories burned across all activities
- **Average Duration**: Mean workout length

### Monthly Activity Chart

An interactive Plotly chart shows your daily workout activities:

- **X-axis**: Days of the current month
- **Y-axis**: Workout metrics (distance, calories, or duration)
- **Color Coding**: Different activity types are color-coded
- **Hover Details**: Hover over data points for detailed workout information

### Activity Type Breakdown

A pie chart or bar chart showing the distribution of your activities:

- Running, cycling, walking, etc.
- Percentage or count of each activity type
- Interactive legend for filtering

### Recent Workouts Table

A scrollable table displaying your most recent workouts with columns:

| Column | Description |
|--------|-------------|
| Date | Workout date and time |
| Activity | Type of workout |
| Distance | Miles covered |
| Duration | Time spent exercising |
| Calories | Energy burned |
| Pace | Average pace (for applicable activities) |

## Interactive Features

### Date Range Selection

Use the date picker widgets to:

- Select specific months or date ranges
- Compare different time periods
- Filter data for focused analysis

### Activity Filtering

Filter your view by activity type:

- Use checkboxes or dropdown menus
- Select multiple activity types
- Clear filters to see all data

### Chart Customization

Customize your visualizations:

- Switch between different chart types
- Adjust time groupings (daily, weekly, monthly)
- Toggle between different metrics (distance, calories, duration)

## Dashboard Widgets

### Progress Indicators

Visual progress bars and indicators show:

- Progress toward monthly goals
- Improvement trends over time
- Performance comparisons

### Calendar Integration

A mini calendar widget allows:

- Quick navigation to specific dates
- Visual indicators for workout days
- Click-through to detailed workout information

### Quick Stats Cards

Informative cards displaying:

- Weekly averages
- Personal records
- Trend indicators (up/down arrows)
- Percentage changes from previous periods

## Customization Options

### Theme Settings

The dashboard supports both light and dark themes:

- Toggle via the settings menu
- Automatic theme detection based on system preferences
- Custom color schemes for different chart types

### Layout Preferences

Customize your dashboard layout:

- Rearrange widget positions
- Show/hide specific sections
- Adjust chart sizes and aspect ratios

### Data Display Options

Control how your data is presented:

- Units (metric vs imperial)
- Date formats
- Number of decimal places
- Chart animation preferences

## Performance Tips

To ensure optimal dashboard performance:

### Large Datasets

- Use date range filters for focused analysis
- Consider aggregating older data
- Utilize the pagination features in data tables

### Refresh Behavior

- The dashboard automatically refreshes when new data is added
- Manual refresh button available in the toolbar
- Real-time updates when connected to live data sources

## Mobile Responsiveness

The dashboard is optimized for various screen sizes:

- **Desktop**: Full feature set with expanded charts
- **Tablet**: Adapted layout with touch-friendly controls
- **Mobile**: Simplified view with essential metrics

### Mobile-Specific Features

- Swipe gestures for chart navigation
- Collapsible sidebar for more screen space
- Touch-optimized date pickers and filters

## Accessibility Features

The dashboard includes accessibility enhancements:

- **Keyboard Navigation**: Full keyboard support for all interactive elements
- **Screen Reader Support**: Proper ARIA labels and descriptions
- **High Contrast Mode**: Enhanced visibility for users with visual impairments
- **Text Scaling**: Respects browser zoom and text size settings

## Data Refresh and Updates

### Automatic Updates

The dashboard automatically reflects changes when:

- New workout data is imported
- Database records are updated
- Configuration changes are applied

### Manual Refresh

Force a data refresh using:

- The refresh button in the interface
- Browser reload (F5)
- Streamlit's rerun functionality

## Troubleshooting Dashboard Issues

### Common Problems

!!! warning "Dashboard Not Loading"
    **Symptoms**: Blank page or loading spinner
    
    **Solutions**:
    - Check database connection
    - Verify Streamlit is running on correct port
    - Review browser console for JavaScript errors

!!! warning "Charts Not Displaying"
    **Symptoms**: Empty chart areas or error messages
    
    **Solutions**:
    - Ensure data exists for selected date range
    - Check for JavaScript or Plotly errors
    - Verify chart configuration settings

!!! warning "Slow Performance"
    **Symptoms**: Delayed responses, timeout errors
    
    **Solutions**:
    - Reduce date range for large datasets
    - Check database query performance
    - Consider data aggregation for historical data

For more detailed troubleshooting, see the [Troubleshooting Reference](../reference/troubleshooting.md).

## Next Steps

Now that you're familiar with the main dashboard:

1. **Import Data**: Learn about [Data Import](data-import.md) options
2. **Advanced Analysis**: Explore the [SQL Query Interface](sql-queries.md)  
3. **Visualizations**: Discover more [Visualization Features](visualizations.md)
4. **Calendar View**: Navigate to the detailed [Calendar interface](../user-guide/dashboard-overview.md)