# Fitness Dashboard User Guide

A web application that helps you understand your workout patterns through intelligent data analysis and visualization.

## What is this?

The Fitness Dashboard takes your exported workout data (from apps like MapMyRun) and helps you discover patterns, track progress, and understand your exercise habits. It uses smart algorithms to automatically categorize your workouts and provides insights about your fitness journey.

## What can you do with it?

- **Import your workout history** from fitness apps
- **View your activity patterns** on interactive dashboards
- **Understand workout types** through automatic categorization
- **Track trends** in your performance over time
- **Explore your data** with flexible visualization tools

## Key Features

### **Smart Workout Analysis**
- Automatically categorizes workouts (running, walking, mixed activities)
- Identifies trends in your performance over time
- Detects unusual patterns or outliers in your data
- Provides confidence scores for all automatic classifications

### **Multiple Dashboard Views**
- **Intelligence Dashboard**: AI-generated insights and recommendations
- **Monthly View**: Traditional calendar and statistics view
- **Trends Analysis**: Statistical charts and performance tracking
- **Data Explorer**: SQL query interface for custom analysis

### **Data Import & Management**
- Import CSV files from MapMyRun and other fitness apps
- Stores 14+ years of workout history
- Flexible data structure for various activity types
- Built-in data validation and quality checks

### **Interactive Features**
- Click on any analysis to see how it was calculated
- Provide feedback to improve automatic categorization
- Explore different time periods and activity types
- Export data and insights for your own use

## Quick Start

Get your fitness dashboard running in minutes:

```bash
# Clone the repository
git clone https://github.com/dagny/fitness-dashboard.git
cd fitness-dashboard

# Install dependencies with Poetry
poetry install

# Set up the database
python scripts/init.py

# Start the application
streamlit run src/streamlit_app.py
```

Visit `http://localhost:8501` to access your dashboard and start exploring:

![Intelligence Dashboard](assets/screenshots/pages/intelligence-dashboard-full.png)

**What you'll see:**
- **Personalized insights** about your workout patterns
- **Automatic workout categorization** with explanations
- **Performance trends** with statistical analysis
- **Interactive data exploration** tools

## Live Demo

Experience the Fitness Dashboard in action at [workouts.barbhs.com](https://workouts.barbhs.com)

## How It Works

The dashboard analyzes your workout data using several techniques:

1. **Data Import**: Upload your workout history from fitness apps
2. **Smart Categorization**: Algorithms automatically classify workout types based on pace, distance, and duration
3. **Pattern Analysis**: Statistical analysis identifies trends and unusual patterns
4. **Interactive Insights**: Click on any result to see how it was calculated

## Understanding the Analysis

### **Workout Categories**
- **Real Runs**: Focused running sessions (typically 8-12 min/mile pace)
- **Walking/Hiking**: Leisurely activities (typically 20-28 min/mile pace)
- **Mixed Activities**: Combined running and walking
- **Outliers**: Unusual workouts that need attention

### **Transparency Features**
Every analysis shows:
- **How it was calculated** - clear explanations of the methods used
- **Confidence levels** - how certain the system is about its conclusions
- **Source information** - where the analysis comes from
- **Feedback options** - ways to improve accuracy

### **Data Quality**
The system automatically:
- **Validates imported data** for completeness and accuracy
- **Identifies potential issues** like missing or unrealistic values
- **Provides suggestions** for improving data quality
- **Tracks changes** over time for consistency

## Getting Started

Ready to analyze your workout data? Here's what to do next:

### **New Users**
1. **[Installation Guide](getting-started/installation.md)** - Set up the dashboard on your computer
2. **[Quick Start](getting-started/quick-start.md)** - Get your first insights in 10 minutes
3. **[Data Import](user-guide/data-import.md)** - Add your workout history

### **Daily Usage**
1. **[Dashboard Overview](user-guide/dashboard-overview.md)** - Understanding the main interface
2. **[Quick Reference](user-guide/quick-reference.md)** - Cheat sheet for common tasks and troubleshooting
3. **[Common Tasks](user-guide/user-journeys.md)** - Step-by-step workflows
4. **[Visualization Features](user-guide/visualizations.md)** - Charts, graphs, and interactive tools

### **Advanced Features**
1. **[Algorithm Transparency](ai/algorithm-transparency.md)** - How the analysis works
2. **[SQL Query Interface](user-guide/sql-queries.md)** - Custom data exploration
3. **[Troubleshooting](reference/troubleshooting.md)** - Common issues and solutions

## Support

- **Questions**: Check the [troubleshooting guide](reference/troubleshooting.md) or browse existing documentation
- **Bug reports**: Submit issues on [GitHub](https://github.com/dagny/fitness-dashboard/issues)
- **Feature requests**: Use the GitHub issues page to suggest improvements
- **Contact**: For other questions, reach out to [barbs@balex.com](mailto:barbs@balex.com)