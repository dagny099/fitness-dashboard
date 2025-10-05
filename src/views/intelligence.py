"""
Intelligence Dashboard - AI-First Fitness Insights Interface

Replaces dash.py with intelligence-focused UI that prominently showcases
AI capabilities, algorithm transparency, and personalized recommendations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.intelligence_service import FitnessIntelligenceService
from services.database_service import DatabaseService
from utils.consistency_analyzer import ConsistencyAnalyzer

# Page configuration
# st.set_page_config(
#     page_title="Your Fitness Intelligence",
#     page_icon="🧠",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Algorithm transparency configuration
ALGORITHM_INFO = {
    'workout_classification': {
        'name': 'K-means ML Classification',
        'icon': '🤖',
        'file': 'intelligence_service.py:75-186',
        'description': 'Automatically categorizes workouts using machine learning clustering based on pace, distance, and duration patterns.'
    },
    'trend_analysis': {
        'name': 'Linear Regression Trends',
        'icon': '📈',
        'file': 'statistics.py:13-79',
        'description': 'Detects performance trends using statistical regression with confidence intervals.'
    },
    'anomaly_detection': {
        'name': 'Statistical Outlier Detection',
        'icon': '🔍',
        'file': 'statistics.py:153-217',
        'description': 'Identifies unusual workouts using IQR, Z-score, and modified Z-score methods.'
    },
    'consistency_analysis': {
        'name': 'Multi-dimensional Scoring',
        'icon': '📊',
        'file': 'consistency_analyzer.py:24-75',
        'description': 'Weighted composite scoring: Frequency (40%) + Timing (20%) + Performance (20%) + Streaks (20%)'
    },
    'forecasting': {
        'name': 'Trend Extrapolation',
        'icon': '🔮',
        'file': 'statistics.py:81-148',
        'description': 'Predicts future performance using linear extrapolation with confidence bands.'
    }
}

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_intelligence_data(time_period='30d'):
    """Load workout data and generate intelligence insights"""
    try:
        intelligence_service = FitnessIntelligenceService()

        # Convert time period to days
        days_map = {'7d': 7, '30d': 30, '90d': 90, '365d': 365}
        days_lookback = days_map.get(time_period, 30)

        brief = intelligence_service.generate_daily_intelligence_brief(days_lookback=days_lookback)

        # Get performance summary for header stats
        summary = intelligence_service.get_performance_summary(time_period)

        return brief, summary
    except Exception as e:
        st.error(f"Failed to load intelligence data: {e}")
        return None, None

def render_algorithm_badge(algorithm_type, confidence=None):
    """Render algorithm transparency badge"""
    if algorithm_type not in ALGORITHM_INFO:
        return ""
    
    algo = ALGORITHM_INFO[algorithm_type]
    confidence_text = f" ({confidence:.0f}% confident)" if confidence else ""
    
    return f"{algo['icon']} {algo['name']}{confidence_text}"

def render_algorithm_tooltip(algorithm_type):
    """Generate algorithm transparency tooltip"""
    if algorithm_type not in ALGORITHM_INFO:
        return "Algorithm information not available"
    
    algo = ALGORITHM_INFO[algorithm_type]
    return f"🔍 Algorithm: {algo['name']}\\n📁 File: {algo['file']}\\n💡 {algo['description']}"

def render_fitness_dashboard_header(total_workouts=0, earliest_date=None, latest_date=None):
    """Render clean dashboard header with title, today's date, and total dataset stats"""
    from datetime import datetime

    today_str = datetime.now().strftime('%B %d, %Y')

    # Format dataset info for right side
    dataset_count = f"Total dataset: {total_workouts:,} workouts" if total_workouts > 0 else ""

    dataset_range = ""
    if earliest_date and latest_date:
        earliest_str = earliest_date.strftime('%m/%d/%Y') if hasattr(earliest_date, 'strftime') else str(earliest_date)[:10]
        latest_str = latest_date.strftime('%m/%d/%Y') if hasattr(latest_date, 'strftime') else str(latest_date)[:10]
        dataset_range = f"From {earliest_str} to {latest_str}"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 25px; border-radius: 15px; color: white; margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <h1 style="margin: 0; font-size: 2.5rem;">🏃‍♀️ Fitness Dashboard</h1>
            <div style="text-align: right; margin-top: 5px;">
                <div style="font-size: 1.1rem; opacity: 0.9; margin-bottom: 12px;">
                    Today is {today_str}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.8; margin-top: 3px;">
                    {dataset_count}
                </div>
                <div style="font-size: 0.85rem; opacity: 0.75; margin-top: 3px;">
                    {dataset_range}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_time_period_selector_and_filter_info(brief):
    """Render time period selector and filter info in a single row with matching heights"""
    from datetime import datetime, timedelta

    period_options = {
        '7d': 'Last 7 days',
        '30d': 'Last 30 days',
        '90d': 'Last 3 months',
        '365d': 'Last year'
    }

    # Create single row layout: dropdown (1 part) + filter info (3 parts)
    col_dropdown, col_filter = st.columns([1, 3])

    with col_dropdown:
        selected_period = st.selectbox(
            "Analysis timeframe:",
            options=list(period_options.keys()),
            format_func=lambda x: period_options[x],
            index=1,  # Default to 30d
            key="intelligence_period"
        )

    with col_filter:
        # Add blank line for spacing to align filter summary with dropdown bottom
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # Get actual date range from intelligence brief if available
        date_range = brief.get('date_range', {}) if brief else {}
        start_date = date_range.get('start_date')
        end_date = date_range.get('end_date')

        # Fallback to calculated dates if not in brief
        if not start_date or not end_date:
            today = datetime.now()
            days_map = {'7d': 7, '30d': 30, '90d': 90, '365d': 365}
            days_back = days_map.get(selected_period, 30)
            end_date = today
            start_date = today - timedelta(days=days_back)
        else:
            # Parse dates from brief
            start_date = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
            end_date = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date

        # Format dates
        start_str = start_date.strftime('%m/%d/%y')
        end_str = end_date.strftime('%m/%d/%y')

        # Get workout count
        recent_workouts = brief.get('recent_workouts_analyzed', 0) if brief else 0

        # Get period display name
        period_name = period_options.get(selected_period, f'{selected_period} period')

        # Render with theme-aware semi-transparent purple background
        st.markdown(f"""
        <div style="background: rgba(102, 126, 234, 0.1);
                    padding: 12px 20px;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                    display: flex;
                    align-items: center;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; width: 100%;">
                <div style="font-size: 0.95rem;">
                    <strong>Filtering workouts:</strong> {start_str} to {end_str}
                </div>
                <div style="font-size: 0.95rem;">
                    <strong>Period:</strong> {period_name}
                </div>
                <div style="font-size: 0.95rem;">
                    <strong>Found:</strong> {recent_workouts:,} workouts
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return selected_period, period_options

def render_data_visibility_expander(brief, time_period):
    """Render expandable section showing the actual workout data being analyzed"""
    with st.expander("📊 View Selected Data", expanded=True):
        # Get the summary data (needed for warning at end)
        total_workouts = brief.get('recent_workouts_analyzed', 0)

        # Show workout breakdown by type if available
        classification_data = brief.get('classification_intelligence', {})
        if 'summary' in classification_data:
            summary = classification_data['summary']
            st.subheader("Workout Classification Breakdown")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Real Runs", summary.get('real_run', 0))
            with col2:
                st.metric("Pup Walks", summary.get('pup_walk', 0))
            with col3:
                st.metric("Mixed Activities", summary.get('mixed', 0))
            with col4:
                st.metric("Outliers", summary.get('outlier', 0))

        # Show actual workout data table with ML classifications
        st.subheader("📋 Individual Workouts & Classifications")

        # Use the SAME data that the intelligence service already calculated
        # This prevents date range inconsistencies between intelligence brief and table

        # Use the EXACT same data that the intelligence service already calculated
        # This prevents date range inconsistencies between intelligence brief and table
        classification_data = brief.get('classification_intelligence', {})

        if 'classified_workouts' in classification_data:
            # Use the exact same data the intelligence algorithms used - no duplicate filtering!
            classified_df = classification_data['classified_workouts'].copy()
        else:
            # No classified data available
            st.warning("Classification data not available. Please check the intelligence service.")
            return

        if not classified_df.empty:
            # Create display dataframe with specific column order
            display_df = classified_df.copy()

            # Add classification if available
            if 'predicted_activity_type' in classified_df.columns:
                display_df['classification'] = classified_df['predicted_activity_type']
            else:
                # Add a fallback classification based on available data
                if 'avg_pace' in display_df.columns:
                    display_df['classification'] = display_df['avg_pace'].apply(
                        lambda x: 'real_run' if pd.notna(x) and x <= 12 else 'pup_walk' if pd.notna(x) else 'unknown'
                    )
                else:
                    display_df['classification'] = 'unknown'

            # Format columns
            if 'workout_date' in display_df.columns:
                display_df['Date'] = pd.to_datetime(display_df['workout_date']).dt.strftime('%m/%d/%y')

            if 'duration_sec' in display_df.columns:
                display_df['Duration'] = display_df['duration_sec'].apply(
                    lambda x: f"{int(x//3600)}h {int((x%3600)//60)}m" if pd.notna(x) else "N/A"
                )

            # Round numeric columns
            if 'distance_mi' in display_df.columns:
                display_df['Distance (Mi)'] = display_df['distance_mi'].round(1)

            if 'avg_pace' in display_df.columns:
                display_df['Pace (min/mi)'] = display_df['avg_pace'].round(1)

            if 'kcal_burned' in display_df.columns:
                display_df['Calories'] = display_df['kcal_burned'].round(0).astype(int)

            # Format ML Classification with proper display names
            display_df['ML Classification'] = display_df['classification'].apply(
                lambda x: {
                    'real_run': 'Run',
                    'pup_walk': 'Walk',
                    'mixed': 'Mixed',
                    'outlier': 'Outlier',
                    'unknown': 'Unknown'
                }.get(x, x)
            )

            # Select and order columns: Date, Duration, Distance (Mi), Pace (min/mi), Calories, ML Classification
            final_columns = []
            if 'Date' in display_df.columns:
                final_columns.append('Date')
            if 'Duration' in display_df.columns:
                final_columns.append('Duration')
            if 'Distance (Mi)' in display_df.columns:
                final_columns.append('Distance (Mi)')
            if 'Pace (min/mi)' in display_df.columns:
                final_columns.append('Pace (min/mi)')
            if 'Calories' in display_df.columns:
                final_columns.append('Calories')
            if 'ML Classification' in display_df.columns:
                final_columns.append('ML Classification')
            # Keep classification column for styling
            if 'classification' in display_df.columns:
                final_columns.append('classification')

            display_df = display_df[final_columns]

            # Sort by date (most recent first)
            if 'Date' in display_df.columns:
                display_df = display_df.sort_values('Date', ascending=False)

            # Apply color styling based on classification (use actual classification values)
            # Create styling function that uses the classification column
            def color_rows(row):
                # Get classification from the full dataframe using the row name (index)
                classification = display_df.loc[row.name, 'classification'] if row.name in display_df.index else 'unknown'

                if classification == 'real_run':
                    color = '#1f77b4'  # Blue for runs
                elif classification == 'pup_walk' or classification == 'mixed':
                    color = '#2ca02c'  # Green for walks and mixed
                elif classification == 'outlier':
                    color = '#d62728'  # Red for outliers
                else:
                    color = '#7f7f7f'  # Gray for unknown
                return [f'color: {color}'] * len(row)

            # Remove classification column before styling (styling function will look it up)
            display_cols = [col for col in final_columns if col != 'classification']
            styled_df = display_df[display_cols].style.apply(color_rows, axis=1)

            # Display the table with styling
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                height=300
            )
        else:
            st.info("No workouts found for the selected time period.")

        # Only show warning for truly empty data
        if total_workouts == 0:
            st.warning("⚠️ No workouts found for selected period. Try selecting a longer timeframe.")

def calculate_concrete_metrics(brief, time_period):
    """Calculate concrete metrics for the period using consistent data from intelligence brief"""
    try:
        # Use the same workout count that the intelligence brief calculated
        total_workouts = brief.get('recent_workouts_analyzed', 0)

        # Get classification data from the brief for consistent metrics
        classification_data = brief.get('classification_intelligence', {})

        if 'summary' in classification_data:
            # Use the classification summary from the brief
            summary = classification_data['summary']
            runs = summary.get('real_run', 0)
            walks = summary.get('pup_walk', 0) + summary.get('mixed', 0)
            other = summary.get('outlier', 0)
        else:
            # Fallback if no classification data
            runs = 0
            walks = 0
            other = total_workouts

        # Get performance metrics from the brief
        performance_data = brief.get('performance_intelligence', {})

        # Extract totals from performance data or use fallback calculation
        total_distance = 0
        total_duration_sec = 0
        total_calories = 0

        # Try to get totals from performance data
        if 'distance_mi' in performance_data:
            dist_data = performance_data['distance_mi']
            if isinstance(dist_data, dict):
                total_distance = dist_data.get('current_total', 0) or dist_data.get('current_average', 0) * total_workouts

        if 'duration_sec' in performance_data:
            dur_data = performance_data['duration_sec']
            if isinstance(dur_data, dict):
                total_duration_sec = dur_data.get('current_total', 0) or dur_data.get('current_average', 0) * total_workouts

        if 'kcal_burned' in performance_data:
            cal_data = performance_data['kcal_burned']
            if isinstance(cal_data, dict):
                total_calories = cal_data.get('current_total', 0) or cal_data.get('current_average', 0) * total_workouts

        # Calculate actual totals from raw data (performance data only has averages)
        from services.intelligence_service import FitnessIntelligenceService
        intelligence_service = FitnessIntelligenceService()

        # Convert time period to days for data loading
        days_map = {'7d': 7, '30d': 30, '90d': 90, '365d': 365}
        days_lookback = days_map.get(time_period, 30)

        # Load the same filtered data that the intelligence service used
        df = intelligence_service._load_workout_data()
        if not df.empty:
            from datetime import datetime, timedelta
            import pandas as pd
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_lookback)

            if df['workout_date'].dtype == 'object':
                df['workout_date'] = pd.to_datetime(df['workout_date'])

            period_df = df[df['workout_date'] >= start_date]

            # Calculate metric totals from actual data, but keep consistent workout count from brief
            # Note: Do NOT override total_workouts - it must match intelligence brief for consistency
            total_distance = period_df['distance_mi'].sum() if 'distance_mi' in period_df.columns else 0
            total_duration_sec = period_df['duration_sec'].sum() if 'duration_sec' in period_df.columns else 0
            total_calories = period_df['kcal_burned'].sum() if 'kcal_burned' in period_df.columns else 0

            # Re-classify workouts for accurate activity mix
            if not period_df.empty:
                classified_df = intelligence_service.classify_workout_types(period_df)
                if 'predicted_activity_type' in classified_df.columns:
                    runs = len(classified_df[classified_df['predicted_activity_type'] == 'real_run'])
                    walks = len(classified_df[classified_df['predicted_activity_type'].isin(['pup_walk', 'mixed'])])
                    other = len(classified_df[classified_df['predicted_activity_type'] == 'outlier'])
                else:
                    # Fallback classification by pace if ML classification unavailable
                    runs = len(period_df[period_df['avg_pace'] <= 12]) if 'avg_pace' in period_df.columns else 0
                    walks = len(period_df[period_df['avg_pace'] > 12]) if 'avg_pace' in period_df.columns else 0
                    other = total_workouts - runs - walks

        # Calculate duration in hours and minutes
        total_hours = int(total_duration_sec // 3600)
        total_minutes = int((total_duration_sec % 3600) // 60)

        return {
            'total_workouts': total_workouts,
            'total_distance': total_distance,
            'total_hours': total_hours,
            'total_minutes': total_minutes,
            'total_calories': int(total_calories),
            'runs': runs,
            'walks': walks,
            'other': other
        }
    except Exception as e:
        st.error(f"Error calculating metrics: {e}")
        return {
            'total_workouts': 0,
            'total_distance': 0.0,
            'total_hours': 0,
            'total_minutes': 0,
            'total_calories': 0,
            'runs': 0,
            'walks': 0,
            'other': 0
        }

def render_concrete_metrics_cards(brief, time_period):
    """Render concrete metrics cards above the fold"""
    metrics = calculate_concrete_metrics(brief, time_period)

    st.subheader("📊 Period Summary")

    # Calculate averages
    avg_duration = metrics['total_hours'] * 60 + metrics['total_minutes']  # in minutes
    avg_duration_per_workout = avg_duration / metrics['total_workouts'] if metrics['total_workouts'] > 0 else 0
    avg_distance_per_workout = metrics['total_distance'] / metrics['total_workouts'] if metrics['total_workouts'] > 0 else 0
    avg_calories_per_workout = metrics['total_calories'] / metrics['total_workouts'] if metrics['total_workouts'] > 0 else 0

    # Row 1: Avg Workouts/Week and averages per workout
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Calculate workout frequency
        days_in_period = int(time_period.replace('d', '')) if 'd' in time_period else 365
        workouts_per_week = (metrics['total_workouts'] / days_in_period) * 7 if days_in_period > 0 else 0
        st.metric(
            label="📈 Avg Workouts/Week",
            value=f"{workouts_per_week:.1f}",
            help="Average workouts per week in this period"
        )

    with col2:
        st.metric(
            label="🏃 Avg Distance/Workout",
            value=f"{avg_distance_per_workout:.1f} mi",
            help="Average distance per workout"
        )

    with col3:
        st.metric(
            label="⏱️ Avg Duration/Workout",
            value=f"{int(avg_duration_per_workout)}m",
            help="Average duration per workout"
        )

    with col4:
        st.metric(
            label="🔥 Avg Calories/Workout",
            value=f"{int(avg_calories_per_workout)}",
            help="Average calories per workout"
        )

    # Row 2: Total workouts count and totals
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric(
            label="📊 Workouts",
            value=metrics['total_workouts'],
            help="Total number of workouts in this period"
        )

    with col6:
        st.metric(
            label="🏃 Total Distance",
            value=f"{metrics['total_distance']:.1f} mi",
            help="Total distance covered"
        )

    with col7:
        duration_text = f"{metrics['total_hours']}h {metrics['total_minutes']}m"
        st.metric(
            label="⏱️ Total Duration",
            value=duration_text,
            help="Total workout time"
        )

    with col8:
        st.metric(
            label="🔥 Total Calories",
            value=f"{metrics['total_calories']:,}",
            help="Total calories burned"
        )

    # Row 3: Activity Mix (3 columns wide for better display)
    col_activity, col_spacer1, col_spacer2, col_spacer3 = st.columns([3, 1, 1, 1])

    with col_activity:
        # Activity mix display with more concise formatting
        if metrics['total_workouts'] > 0:
            # Use shorter format to prevent text cutoff
            parts = []
            if metrics['runs'] > 0:
                parts.append(f"{metrics['runs']} Run{'s' if metrics['runs'] != 1 else ''}")
            if metrics['walks'] > 0:
                parts.append(f"{metrics['walks']} Walk{'s' if metrics['walks'] != 1 else ''}")
            if metrics['other'] > 0:
                parts.append(f"{metrics['other']} Other")

            activity_text = ", ".join(parts) if parts else "No activities"
        else:
            activity_text = "No data"

        st.metric(
            label="🏃‍♀️ Activity Mix",
            value=activity_text,
            help="Breakdown of workout types"
        )

def render_key_insights_above_fold(brief):
    """Render key insights above the fold in 2x2 grid - these are the main actionable insights"""
    insights = brief.get('key_insights', [])
    if insights:
        st.subheader("🔍 Key Patterns")

        # Organize insights into 2x2 grid
        # Pad insights to ensure we have at least 4
        while len(insights) < 4:
            insights.append("No additional patterns detected")

        # First row
        col1, col2 = st.columns(2)
        with col1:
            st.info(insights[0])
        with col2:
            if len(insights) > 1:
                st.info(insights[1])

        # Second row
        col3, col4 = st.columns(2)
        with col3:
            if len(insights) > 2:
                st.info(insights[2])
        with col4:
            if len(insights) > 3:
                st.info(insights[3])

def render_intelligence_brief_cards(brief, time_period='30d'):
    """Render visual-first intelligence brief cards with 4 categories"""
    if not brief:
        st.error("Unable to generate intelligence brief")
        return

    period_options = {
        '7d': 'Last 7 days',
        '30d': 'Last 30 days',
        '90d': 'Last 3 months',
        '365d': 'Last year'
    }

    st.subheader(f"📊 Intelligence Brief - {period_options[time_period]}")

    # New analytical sections with insights and visualizations
    render_performance_analysis_section(brief, time_period)

    st.markdown("---")

    render_consistency_analysis_section(brief, time_period)

def render_performance_analysis_section(brief, time_period):
    """Render comprehensive Performance Analysis section with insights and visualizations"""
    st.subheader("🏃 Performance Analysis")

    performance_data = brief.get('performance_intelligence', {})

    # Get actual workout data for visualization
    from services.intelligence_service import FitnessIntelligenceService
    intelligence_service = FitnessIntelligenceService()

    try:
        # Load and filter data
        df = intelligence_service._load_workout_data()
        if df.empty:
            st.warning("No workout data available for performance analysis.")
            return

        from datetime import datetime, timedelta
        import pandas as pd

        days_map = {'7d': 7, '30d': 30, '90d': 90, '365d': 365}
        days_lookback = days_map.get(time_period, 30)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_lookback)

        if df['workout_date'].dtype == 'object':
            df['workout_date'] = pd.to_datetime(df['workout_date'])

        period_df = df[df['workout_date'] >= start_date].copy()

        if period_df.empty:
            st.info("No workouts found in the selected time period.")
            return

        # Apply ML classification
        classified_df = intelligence_service.classify_workout_types(period_df)

        # Separate data by activity type
        runs_df = classified_df[classified_df['predicted_activity_type'] == 'real_run'] if 'predicted_activity_type' in classified_df.columns else pd.DataFrame()
        walks_df = classified_df[classified_df['predicted_activity_type'].isin(['pup_walk', 'mixed'])] if 'predicted_activity_type' in classified_df.columns else pd.DataFrame()

        # Get previous period data for comparison
        previous_start = start_date - timedelta(days=days_lookback)
        previous_period_df = df[(df['workout_date'] >= previous_start) & (df['workout_date'] < start_date)].copy()

        if not previous_period_df.empty:
            previous_classified_df = intelligence_service.classify_workout_types(previous_period_df)
            prev_runs_df = previous_classified_df[previous_classified_df['predicted_activity_type'] == 'real_run'] if 'predicted_activity_type' in previous_classified_df.columns else pd.DataFrame()
            prev_walks_df = previous_classified_df[previous_classified_df['predicted_activity_type'].isin(['pup_walk', 'mixed'])] if 'predicted_activity_type' in previous_classified_df.columns else pd.DataFrame()
        else:
            prev_runs_df = pd.DataFrame()
            prev_walks_df = pd.DataFrame()

        # Render performance cards using Streamlit native components
        period_name = {'7d': 'Last 7 days', '30d': 'Last 30 days', '90d': 'Last 3 months', '365d': 'Last year'}.get(time_period, time_period)
        st.markdown(f"**{period_name} Performance by Activity Type**")

        col1, col2 = st.columns(2)

        # RUN PERFORMANCE CARD (native Streamlit)
        with col1:
            if not runs_df.empty:
                # Calculate current period stats
                run_count = len(runs_df)
                run_distance = runs_df['distance_mi'].sum() if 'distance_mi' in runs_df.columns else 0
                run_avg_distance = runs_df['distance_mi'].mean() if 'distance_mi' in runs_df.columns else 0
                run_avg_pace = runs_df['avg_pace'].mean() if 'avg_pace' in runs_df.columns else 0
                run_pace_range = f"{runs_df['avg_pace'].min():.1f}-{runs_df['avg_pace'].max():.1f}" if 'avg_pace' in runs_df.columns and len(runs_df) > 1 else "N/A"
                run_total_duration = runs_df['duration_sec'].sum() / 3600 if 'duration_sec' in runs_df.columns else 0
                run_avg_duration = runs_df['duration_sec'].mean() / 60 if 'duration_sec' in runs_df.columns else 0
                run_total_calories = runs_df['kcal_burned'].sum() if 'kcal_burned' in runs_df.columns else 0
                run_avg_calories = runs_df['kcal_burned'].mean() if 'kcal_burned' in runs_df.columns else 0

                # Calculate previous period comparison
                prev_run_count = len(prev_runs_df) if not prev_runs_df.empty else 0
                prev_run_avg_pace = prev_runs_df['avg_pace'].mean() if not prev_runs_df.empty and 'avg_pace' in prev_runs_df.columns else None
                prev_run_avg_distance = prev_runs_df['distance_mi'].mean() if not prev_runs_df.empty and 'distance_mi' in prev_runs_df.columns else None

                count_delta = run_count - prev_run_count if prev_run_count > 0 else 0
                pace_delta = (run_avg_pace - prev_run_avg_pace) if prev_run_avg_pace else None
                distance_delta = (run_avg_distance - prev_run_avg_distance) if prev_run_avg_distance else None

                # Native Streamlit container
                with st.container():
                    st.markdown("### 🏃 Run Performance")

                    # Row 1: Count and Distance
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Count", run_count,
                                 delta=f"{count_delta:+d} vs prev" if prev_run_count > 0 else None,
                                 help="Number of runs in this period")
                    with c2:
                        st.metric("Total Distance", f"{run_distance:.1f} mi",
                                 delta=f"Avg: {run_avg_distance:.1f} mi",
                                 help="Total and average distance per run")

                    # Row 2: Pace (with inverse delta) and Range
                    c3, c4 = st.columns(2)
                    with c3:
                        st.metric("Avg Pace", f"{run_avg_pace:.1f} min/mi",
                                 delta=f"{pace_delta:.1f} min/mi" if pace_delta else None,
                                 delta_color="inverse" if pace_delta else "off",
                                 help="Lower pace is better (faster)")
                    with c4:
                        st.metric("Pace Range", f"{run_pace_range} min/mi",
                                 help="Min-Max pace range")

                    # Row 3: Duration and Calories
                    c5, c6 = st.columns(2)
                    with c5:
                        st.metric("Total Duration", f"{run_total_duration:.1f}h",
                                 delta=f"Avg: {run_avg_duration:.0f} min")
                    with c6:
                        st.metric("Total Calories", f"{run_total_calories:,.0f}",
                                 delta=f"Avg: {run_avg_calories:.0f}")

                    st.divider()
            else:
                st.info("🏃 No runs in this period")

        # WALK PERFORMANCE CARD (native Streamlit)
        with col2:
            if not walks_df.empty:
                # Calculate current period stats
                walk_count = len(walks_df)
                walk_distance = walks_df['distance_mi'].sum() if 'distance_mi' in walks_df.columns else 0
                walk_avg_distance = walks_df['distance_mi'].mean() if 'distance_mi' in walks_df.columns else 0
                walk_avg_pace = walks_df['avg_pace'].mean() if 'avg_pace' in walks_df.columns else 0
                walk_pace_range = f"{walks_df['avg_pace'].min():.1f}-{walks_df['avg_pace'].max():.1f}" if 'avg_pace' in walks_df.columns and len(walks_df) > 1 else "N/A"
                walk_total_duration = walks_df['duration_sec'].sum() / 3600 if 'duration_sec' in walks_df.columns else 0
                walk_avg_duration = walks_df['duration_sec'].mean() / 60 if 'duration_sec' in walks_df.columns else 0
                walk_total_calories = walks_df['kcal_burned'].sum() if 'kcal_burned' in walks_df.columns else 0
                walk_avg_calories = walks_df['kcal_burned'].mean() if 'kcal_burned' in walks_df.columns else 0

                # Calculate previous period comparison
                prev_walk_count = len(prev_walks_df) if not prev_walks_df.empty else 0
                prev_walk_avg_pace = prev_walks_df['avg_pace'].mean() if not prev_walks_df.empty and 'avg_pace' in prev_walks_df.columns else None
                prev_walk_avg_distance = prev_walks_df['distance_mi'].mean() if not prev_walks_df.empty and 'distance_mi' in prev_walks_df.columns else None

                count_delta = walk_count - prev_walk_count if prev_walk_count > 0 else 0
                pace_delta = (walk_avg_pace - prev_walk_avg_pace) if prev_walk_avg_pace else None
                distance_delta = (walk_avg_distance - prev_walk_avg_distance) if prev_walk_avg_distance else None

                # Native Streamlit container
                with st.container():
                    st.markdown("### 🚶 Walk Performance")

                    # Row 1: Count and Distance
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Count", walk_count,
                                 delta=f"{count_delta:+d} vs prev" if prev_walk_count > 0 else None,
                                 help="Number of walks in this period")
                    with c2:
                        st.metric("Total Distance", f"{walk_distance:.1f} mi",
                                 delta=f"Avg: {walk_avg_distance:.1f} mi",
                                 help="Total and average distance per walk")

                    # Row 2: Pace and Range
                    c3, c4 = st.columns(2)
                    with c3:
                        st.metric("Avg Pace", f"{walk_avg_pace:.1f} min/mi",
                                 delta=f"{pace_delta:.1f} min/mi" if pace_delta else None,
                                 delta_color="inverse" if pace_delta else "off",
                                 help="Lower pace is better (faster)")
                    with c4:
                        st.metric("Pace Range", f"{walk_pace_range} min/mi",
                                 help="Min-Max pace range")

                    # Row 3: Duration and Calories
                    c5, c6 = st.columns(2)
                    with c5:
                        st.metric("Total Duration", f"{walk_total_duration:.1f}h",
                                 delta=f"Avg: {walk_avg_duration:.0f} min")
                    with c6:
                        st.metric("Total Calories", f"{walk_total_calories:,.0f}",
                                 delta=f"Avg: {walk_avg_calories:.0f}")

                    st.divider()
            else:
                st.info("🚶 No walks in this period")

        # Keep the visualization below the cards
        st.markdown("**📈 Performance Trends**")

        # Create performance trend chart
        try:
            import plotly.express as px
            import plotly.graph_objects as go

            # Prepare data for visualization
            chart_df = classified_df.copy()
            chart_df['workout_date'] = pd.to_datetime(chart_df['workout_date'])
            chart_df = chart_df.sort_values('workout_date')

            # Create trend chart showing distance over time, colored by activity type
            if 'distance_mi' in chart_df.columns and 'predicted_activity_type' in chart_df.columns:
                fig = px.scatter(
                    chart_df,
                    x='workout_date',
                    y='distance_mi',
                    color='predicted_activity_type',
                    title='Distance Trends Over Time',
                    labels={
                        'workout_date': 'Date',
                        'distance_mi': 'Distance (mi)',
                        'predicted_activity_type': 'Activity Type'
                    },
                    color_discrete_map={
                        'real_run': '#1f77b4',
                        'pup_walk': '#2ca02c',
                        'mixed': '#ff7f0e',
                        'outlier': '#d62728'
                    }
                )

                # Add trend lines
                if not runs_df.empty and 'distance_mi' in runs_df.columns:
                    runs_df_sorted = runs_df.sort_values('workout_date')
                    fig.add_scatter(
                        x=runs_df_sorted['workout_date'],
                        y=runs_df_sorted['distance_mi'].rolling(window=3, center=True).mean(),
                        mode='lines',
                        name='Runs Trend',
                        line=dict(color='#1f77b4', dash='dash')
                    )

                if not walks_df.empty and 'distance_mi' in walks_df.columns:
                    walks_df_sorted = walks_df.sort_values('workout_date')
                    fig.add_scatter(
                        x=walks_df_sorted['workout_date'],
                        y=walks_df_sorted['distance_mi'].rolling(window=3, center=True).mean(),
                        mode='lines',
                        name='Walks Trend',
                        line=dict(color='#2ca02c', dash='dash')
                    )

                fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Distance data not available for visualization")

        except ImportError:
            st.info("Install plotly for interactive charts: `pip install plotly`")
        except Exception as e:
            st.info(f"Chart unavailable: {str(e)}")

    except Exception as e:
        st.error(f"Error in performance analysis: {str(e)}")

def render_consistency_analysis_section(brief, time_period):
    """Render comprehensive Consistency Analysis section with insights and visualizations"""
    st.subheader("🔄 Consistency Analysis")

    consistency_data = brief.get('consistency_intelligence', {})

    # Get actual workout data for visualization
    from services.intelligence_service import FitnessIntelligenceService
    intelligence_service = FitnessIntelligenceService()

    try:
        # Load and filter data
        df = intelligence_service._load_workout_data()
        if df.empty:
            st.warning("No workout data available for consistency analysis.")
            return

        from datetime import datetime, timedelta
        import pandas as pd

        days_map = {'7d': 7, '30d': 30, '90d': 90, '365d': 365}
        days_lookback = days_map.get(time_period, 30)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_lookback)

        if df['workout_date'].dtype == 'object':
            df['workout_date'] = pd.to_datetime(df['workout_date'])

        period_df = df[df['workout_date'] >= start_date].copy()

        if period_df.empty:
            st.info("No workouts found in the selected time period.")
            return

        # Create two columns: insights on left, visualization on right
        col_insights, col_visual = st.columns([3, 2])

        with col_insights:
            st.markdown("**📊 Consistency Insights**")

            # Get consistency score
            consistency_score_data = consistency_data.get('consistency_score', 0)
            if isinstance(consistency_score_data, dict):
                consistency_score = consistency_score_data.get('consistency_score', 0)
            else:
                consistency_score = consistency_score_data

            # Data source clarity
            total_workouts = len(period_df)
            workout_frequency = (total_workouts / days_lookback) * 7 if days_lookback > 0 else 0

            st.markdown(f"*Analyzing {total_workouts} workouts over {days_lookback} days*")

            # Consistency score with breakdown
            if consistency_score >= 80:
                level = "Excellent"
                color = "#27ae60"
                insight = "Top-tier consistency - excellent rhythm!"
            elif consistency_score >= 60:
                level = "Good"
                color = "#f39c12"
                insight = "Solid consistency with room for optimization"
            else:
                level = "Building"
                color = "#e74c3c"
                insight = "Building consistency habits"

            st.metric(
                label="Overall Consistency Score",
                value=f"{consistency_score:.0f}/100",
                delta=f"{level} level",
                help="Composite score based on frequency, timing patterns, performance stability, and streaks"
            )

            st.metric(
                label="Workout Frequency",
                value=f"{workout_frequency:.1f}/week",
                help="Average workouts per week in this period"
            )

            # Consistency score breakdown
            st.markdown(f"""
            <div style="padding: 10px; background: {color}15; border-radius: 8px; border-left: 3px solid {color}; margin: 10px 0;">
                <div style="font-size: 0.9rem; color: {color}; font-weight: 600;">🏆 Consistency Breakdown:</div>
                <div style="font-size: 0.85rem; margin-top: 5px; line-height: 1.4;">
                    • <strong>Frequency:</strong> How often you work out<br>
                    • <strong>Timing:</strong> Regular day-of-week patterns<br>
                    • <strong>Performance:</strong> Stable effort levels<br>
                    • <strong>Streaks:</strong> Maintaining workout chains
                </div>
                <div style="font-style: italic; margin-top: 8px; color: #666;">{insight}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_visual:
            st.markdown("**📅 Workout Rhythm Patterns**")

            try:
                import plotly.express as px
                import plotly.graph_objects as go

                # Create workout frequency by day of week
                period_df['day_of_week'] = period_df['workout_date'].dt.day_name()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

                day_counts = period_df['day_of_week'].value_counts().reindex(day_order, fill_value=0)

                # Create bar chart of workouts by day of week
                fig = px.bar(
                    x=day_counts.index,
                    y=day_counts.values,
                    title='Workouts by Day of Week',
                    labels={'x': 'Day of Week', 'y': 'Number of Workouts'},
                    color=day_counts.values,
                    color_continuous_scale='Blues'
                )

                fig.update_layout(
                    height=250,
                    margin=dict(l=0, r=0, t=30, b=40),
                    showlegend=False
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

                # Create calendar heatmap if we have enough data
                if len(period_df) > 5:
                    st.markdown("**📈 Workout Calendar**")

                    # Create a simple workout frequency indicator
                    period_df['date_only'] = period_df['workout_date'].dt.date
                    daily_counts = period_df.groupby('date_only').size()

                    # Show recent workout pattern
                    recent_days = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
                    workout_pattern = []
                    for day in recent_days[-14:]:  # Show last 14 days
                        count = daily_counts.get(day, 0)
                        workout_pattern.append(f"{'🟢' if count > 0 else '⚪'}")

                    st.markdown(f"**Last 14 days:** {''.join(workout_pattern)}")
                    st.caption("🟢 = Workout day, ⚪ = Rest day")

            except ImportError:
                st.info("Install plotly for interactive charts")
            except Exception as e:
                st.info(f"Visualization unavailable: {str(e)}")

    except Exception as e:
        st.error(f"Error in consistency analysis: {str(e)}")

def render_performance_card_legacy(brief, time_period):
    """Render performance trends card with clear, non-conflicting visual indicators"""
    performance_data = brief.get('performance_intelligence', {})

    # Find the best trending metric with highest confidence
    best_metric = 'Distance Mi'
    trend_confidence = 75
    current_avg = 3.3
    pct_change = 6.6
    trend_direction = 'ascending'

    for metric, data in performance_data.items():
        if isinstance(data, dict) and 'trend' in data:
            trend_info = data['trend']
            confidence = trend_info.get('confidence', 0)
            if confidence > trend_confidence:
                trend_confidence = confidence
                best_metric = metric.replace('_', ' ').title()
                trend_direction = trend_info.get('trend_direction', 'stable')
                current_avg = data.get('current_average', 0)
                historical_avg = data.get('historical_average', 0)
                # Calculate percentage change vs historical
                if historical_avg > 0:
                    pct_change = ((current_avg - historical_avg) / historical_avg) * 100
                else:
                    pct_change = 0

    # Determine consistent visual indicators based on actual trend direction
    if trend_direction == 'ascending':
        color = "#27ae60"
        trend_emoji = "📈"
        trend_status = "Improving Trend"
        trend_description = f"Performance is trending upward with {trend_confidence:.0f}% confidence"
    elif trend_direction == 'descending':
        color = "#e74c3c"
        trend_emoji = "📉"
        trend_status = "Declining Trend"
        trend_description = f"Performance is trending downward with {trend_confidence:.0f}% confidence"
    else:
        color = "#3498db"
        trend_emoji = "📊"
        trend_status = "Stable Trend"
        trend_description = f"Performance is stable with {trend_confidence:.0f}% confidence"

    # Create card with consistent visual theme
    with st.container():
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color}15 0%, {color}08 100%);
                    border-left: 4px solid {color}; padding: 18px; border-radius: 10px; margin-bottom: 10px;">
            <h4 style="color: {color}; margin: 0 0 10px 0; font-size: 1rem;">🏃 Performance Analysis - {time_period.replace('d', ' days').replace('365 days', '1 year')}</h4>
        </div>
        """, unsafe_allow_html=True)

        # Main performance metric with clear context
        col1, col2 = st.columns([3, 1])
        with col1:
            st.metric(
                label=f"Current {best_metric} Average",
                value=f"{current_avg:.1f}",
                delta=f"{pct_change:+.1f}% vs historical average",
                help=f"Comparing current {time_period} average to your historical performance"
            )

            # Clear trend status
            st.markdown(f"""
            <div style="margin: 10px 0; padding: 8px; background: {color}20; border-radius: 5px;">
                <strong style="color: {color};">📊 Trend Status:</strong> {trend_status}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div style='font-size: 3rem; text-align: center; margin-top: 15px;'>{trend_emoji}</div>", unsafe_allow_html=True)

        # Add future outlook section
        st.markdown("---")

        # Future outlook using predictive intelligence
        predictive_data = brief.get('predictive_intelligence', {})
        forecast_confidence = 70
        forecast_direction = 'stable'

        # Find best forecast for the same metric
        for metric, data in predictive_data.items():
            if isinstance(data, dict) and 'forecast' in data:
                forecast_info = data['forecast']
                if isinstance(forecast_info, dict):
                    confidence = forecast_info.get('confidence', 0)
                    if confidence > forecast_confidence and metric.replace('_', ' ').title() == best_metric:
                        forecast_confidence = confidence
                        forecast_direction = forecast_info.get('trend_direction', 'stable')

        # Future outlook display
        if forecast_direction == 'ascending':
            outlook_color = "#27ae60"
            outlook_icon = "📈"
            outlook_text = "Positive outlook"
        elif forecast_direction == 'descending':
            outlook_color = "#e74c3c"
            outlook_icon = "📉"
            outlook_text = "Declining outlook"
        else:
            outlook_color = "#3498db"
            outlook_icon = "📊"
            outlook_text = "Stable outlook"

        # Concise future outlook
        st.markdown(f"""
        <div style="padding: 6px 12px; background: {outlook_color}12; border-radius: 8px; border-left: 3px solid {outlook_color}; margin-top: 8px;">
            <span style="font-size: 0.85rem; color: {outlook_color}; font-weight: 600;">
                🔮 14-Day Outlook: {outlook_text} ({forecast_confidence:.0f}% confidence)
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Algorithm transparency
        algorithm_badge = render_algorithm_badge('trend_analysis', trend_confidence)
        st.info(f"{algorithm_badge}")
        st.markdown(f"<div style='font-size: 0.85rem; color: #666;'>{trend_description}</div>", unsafe_allow_html=True)

    with st.expander("📈 How are trends calculated?"):
        st.markdown(f"""
        **Algorithm:** {ALGORITHM_INFO['trend_analysis']['name']}
        **Confidence:** {trend_confidence:.0f}%
        **Metric:** {best_metric}

        **Process:**
        1. Linear regression on {time_period} data
        2. Calculate slope and correlation
        3. Statistical significance testing
        4. Compare current vs historical averages
        """)

def render_consistency_card(brief, time_period):
    """Render consistency analysis card with clear score explanation and legible metrics"""
    consistency_data = brief.get('consistency_intelligence', {})
    consistency_score_data = consistency_data.get('consistency_score', 0)

    # Handle case where consistency_score is a dict or number
    if isinstance(consistency_score_data, dict):
        consistency_score = consistency_score_data.get('consistency_score', 0)
    else:
        consistency_score = consistency_score_data

    # Calculate insights based on score
    if consistency_score >= 80:
        level = "Excellent"
        color = "#27ae60"
        icon = "🏆"
        insight = "Top-tier consistency - you're crushing it!"
        level_description = "Excellent rhythm and reliability"
    elif consistency_score >= 60:
        level = "Good"
        color = "#f39c12"
        icon = "📊"
        insight = "Solid consistency with room for improvement"
        level_description = "Good foundation, optimize timing & frequency"
    else:
        level = "Building"
        color = "#e74c3c"
        icon = "🎯"
        insight = "Building consistency habits"
        level_description = "Focus on regular workout patterns"

    # Calculate workout frequency (more robust calculation)
    total_workouts = brief.get('recent_workouts_analyzed', 0)
    days_in_period = int(time_period.replace('d', '')) if 'd' in time_period else 365
    freq_per_week = (total_workouts / days_in_period) * 7 if days_in_period > 0 else 0

    # Use Streamlit container with clear explanations
    with st.container():
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color}15 0%, {color}08 100%);
                    border-left: 4px solid {color}; padding: 18px; border-radius: 10px; margin-bottom: 10px;">
            <h4 style="color: {color}; margin: 0 0 10px 0; font-size: 1rem;">🔄 Consistency Analysis - {time_period.replace('d', ' days').replace('365 days', '1 year')}</h4>
        </div>
        """, unsafe_allow_html=True)

        # Clear score explanation and metrics
        col1, col2 = st.columns([2, 1])
        with col1:
            # Consistency score with clear explanation
            st.metric(
                label="Overall Consistency Score",
                value=f"{consistency_score:.0f}/100",
                delta=f"{level} level",
                help="Composite score based on workout frequency, timing patterns, performance stability, and streak maintenance"
            )

            # Score breakdown in a more visible format
            st.markdown(f"""
            <div style="margin: 12px 0; padding: 10px; background: {color}15; border-radius: 5px; border-left: 3px solid {color};">
                <div style="font-size: 0.9rem; color: {color}; font-weight: 600;">📊 Score Breakdown:</div>
                <div style="font-size: 0.85rem; margin-top: 5px; line-height: 1.4;">
                    • <strong>Frequency:</strong> How often you work out<br>
                    • <strong>Timing:</strong> Regular day-of-week patterns<br>
                    • <strong>Performance:</strong> Stable effort levels<br>
                    • <strong>Streaks:</strong> Maintaining workout chains
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Large, legible frequency metric
            st.markdown(f"<div style='text-align: center; margin-top: 20px;'>{icon}</div>", unsafe_allow_html=True)

            # Clear frequency display
            st.markdown(f"""
            <div style="text-align: center; margin: 15px 0;">
                <div style="font-size: 1.8rem; font-weight: bold; color: {color};">{freq_per_week:.1f}</div>
                <div style="font-size: 0.9rem; color: #666;">workouts/week</div>
                <div style="font-size: 0.8rem; color: #888;">{total_workouts} total workouts</div>
            </div>
            """, unsafe_allow_html=True)

        # Algorithm transparency and insight
        algorithm_badge = render_algorithm_badge('consistency_analysis', consistency_score)
        st.info(f"{algorithm_badge}")
        st.markdown(f"<div style='font-size: 0.9rem; color: #666; font-style: italic;'>{insight}</div>", unsafe_allow_html=True)

    with st.expander("🔄 How is consistency calculated?"):
        st.markdown(f"""
        **Algorithm:** Multi-dimensional Scoring
        **Score:** {consistency_score:.0f}/100

        **Components:**
        - Frequency (40%): Workout regularity
        - Timing (20%): Day-of-week patterns
        - Performance (20%): Metric stability
        - Streaks (20%): Current vs historical
        """)


def render_insights_card(brief, time_period):
    """Render key insights card with visual context"""
    anomaly_data = brief.get('anomaly_intelligence', {})
    total_anomalies = anomaly_data.get('summary', {}).get('total_anomalies_detected', 0)
    recent_anomalies = anomaly_data.get('summary', {}).get('recent_anomalies', 0)

    # Determine status based on anomalies and insights
    insights = brief.get('key_insights', [])
    insights_count = len(insights)

    if recent_anomalies > 0:
        status = f"{recent_anomalies} anomalies detected"
        color = "#f39c12"
        icon = "⚠️"
        detail = "Some workouts outside normal patterns"
    elif insights_count >= 3:
        status = f"{insights_count} insights discovered"
        color = "#27ae60"
        icon = "💡"
        detail = "Rich intelligence from your data"
    else:
        status = "Building intelligence"
        color = "#3498db"
        icon = "🧠"
        detail = "Collecting data for deeper insights"

    # Use Streamlit container instead of raw HTML
    with st.container():
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color}15 0%, {color}08 100%);
                    border-left: 4px solid {color}; padding: 18px; border-radius: 10px; margin-bottom: 10px;">
            <h4 style="color: {color}; margin: 0 0 10px 0; font-size: 1rem;">💡 Insights - {time_period.replace('d', ' days').replace('365 days', '1 year')}</h4>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{status.title()}**")
            # Show metrics in larger text above detail
            st.markdown(f"<div style='font-size: 1.1rem; font-weight: 500; margin: 8px 0;'>{detail}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='font-size: 2rem; text-align: center;'>{icon}</div>", unsafe_allow_html=True)

        algorithm_badge = render_algorithm_badge('anomaly_detection')
        st.info(f"{algorithm_badge}")
        st.markdown(f"<div style='font-size: 0.85rem; color: #666;'>AI-powered pattern recognition</div>", unsafe_allow_html=True)

    with st.expander("🔍 How are insights generated?"):
        st.markdown(f"""
        **Algorithm:** Multi-algorithm Analysis
        **Insights found:** {insights_count}
        **Anomalies:** {recent_anomalies}

        **Analysis methods:**
        - Statistical outlier detection
        - Pattern recognition algorithms
        - Performance trend analysis
        - Behavioral insight generation
        """)


def main():
    """Main intelligence dashboard application"""

    # Custom CSS for intelligence dashboard
    st.markdown("""
    <style>
    .metric-card {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: white;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .algorithm-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        background: #f0f0f0;
        font-size: 0.8rem;
        color: #666;
        margin: 5px 0;
    }

    .confidence-high { background: linear-gradient(135deg, #27ae60, #2ecc71); }
    .confidence-medium { background: linear-gradient(135deg, #f39c12, #f1c40f); }
    .confidence-low { background: linear-gradient(135deg, #e74c3c, #ec7063); }
    </style>
    """, unsafe_allow_html=True)

    # Get total dataset stats for header (static, calculated once)
    from services.database_service import DatabaseService
    from datetime import datetime

    try:
        db = DatabaseService()
        query = 'SELECT COUNT(*) as total, MIN(workout_date) as earliest, MAX(workout_date) as latest FROM workout_summary'
        results = db.execute_query(query)
        total_workouts = results[0]['total']
        earliest_date = results[0]['earliest']
        latest_date = results[0]['latest']
    except Exception as e:
        st.error(f"Failed to load dataset stats: {e}")
        total_workouts = 0
        earliest_date = None
        latest_date = None

    # Render header with total dataset stats
    render_fitness_dashboard_header(total_workouts, earliest_date, latest_date)

    # Load initial intelligence data (using default 30d period)
    brief, summary = load_intelligence_data('30d')

    if not brief:
        st.error("Failed to load intelligence data. Please check your database connection.")
        return

    # Combined time period selector and filter info (single row)
    selected_period, period_options = render_time_period_selector_and_filter_info(brief)

    # Reload intelligence data if period changed
    if selected_period != '30d':
        brief, summary = load_intelligence_data(selected_period)

    # Concrete metrics cards - above the fold
    render_concrete_metrics_cards(brief, selected_period)

    # Show data visibility expander between Period Summary and Key Patterns
    render_data_visibility_expander(brief, selected_period)

    # Key insights - above the fold
    render_key_insights_above_fold(brief)

    st.markdown("---")

    # Intelligence brief cards (algorithmic analysis)
    render_intelligence_brief_cards(brief, selected_period)

    st.markdown("---")

    # AI Recommendations section (will be replaced with Personalized Goals)
    st.subheader("🎯 Personalized AI Recommendations")
    
    recommendations = brief.get('recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations[:3]):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{i+1}. {rec}**")
                
                with col2:
                    if st.button(f"Try This", key=f"rec_{i}"):
                        st.success("Added to your plan!")
    
    # Key insights now appear above the fold

    # Footer with technical details
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.9rem;">
        <p><strong>Fitness Intelligence System</strong> • Powered by Machine Learning & Statistical Analysis</p>
        <p>🤖 K-means Classification • 📈 Linear Regression • 🔍 Anomaly Detection • 📊 Multi-dimensional Analysis</p>
        <p><em>Full algorithm transparency available in documentation</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()