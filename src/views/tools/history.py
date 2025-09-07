import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.database_service import DatabaseService

st.markdown("# 🏃‍♀️ Workout History")
st.markdown("*Complete history of all your workout activities*")

@st.cache_data
def load_workout_data():
    """Load workout data from database"""
    try:
        db_service = DatabaseService()
        
        query = """
        SELECT workout_date, activity_type, kcal_burned, distance_mi, 
               duration_sec, avg_pace, max_pace, steps, link
        FROM workout_summary 
        ORDER BY workout_date DESC
        """
        
        with db_service.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            
            # Convert to DataFrame manually
            if rows:
                df = pd.DataFrame(rows)
                # workout_date is already datetime, no conversion needed
                df['duration_min'] = (df['duration_sec'] / 60).round(1)
                return df
            else:
                return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error loading workout data: {str(e)}")
        return pd.DataFrame()

# Load data
df = load_workout_data()

if df.empty:
    st.warning("No workout data found. Make sure your database is properly configured and contains workout data.")
    st.stop()

# Sidebar filters
st.sidebar.markdown("### 🔍 Filter Options")

# Date range filter
min_date = df['workout_date'].min()
max_date = df['workout_date'].max()

# Handle datetime to date conversion safely
if hasattr(min_date, 'date'):
    min_date_val = min_date.date()
    max_date_val = max_date.date()
else:
    min_date_val = min_date
    max_date_val = max_date

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date_val, max_date_val),
    min_value=min_date_val,
    max_value=max_date_val
)

# Activity type filter
activity_types = ['All'] + sorted(df['activity_type'].unique().tolist())
selected_activity = st.sidebar.selectbox("Activity Type", activity_types)

# Apply filters
filtered_df = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    # Convert workout_date to date for comparison if it's datetime
    if hasattr(filtered_df['workout_date'].iloc[0], 'date'):
        filtered_df = filtered_df[
            (filtered_df['workout_date'].apply(lambda x: x.date()) >= start_date) & 
            (filtered_df['workout_date'].apply(lambda x: x.date()) <= end_date)
        ]
    else:
        filtered_df = filtered_df[
            (filtered_df['workout_date'] >= start_date) & 
            (filtered_df['workout_date'] <= end_date)
        ]

if selected_activity != 'All':
    filtered_df = filtered_df[filtered_df['activity_type'] == selected_activity]

# Summary metrics
if not filtered_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Workouts",
            len(filtered_df),
            delta=None
        )
    
    with col2:
        total_calories = filtered_df['kcal_burned'].sum()
        st.metric(
            "Total Calories",
            f"{total_calories:,}",
            delta=None
        )
    
    with col3:
        total_distance = filtered_df['distance_mi'].sum()
        st.metric(
            "Total Distance",
            f"{total_distance:.1f} mi",
            delta=None
        )
    
    with col4:
        total_duration = filtered_df['duration_min'].sum()
        st.metric(
            "Total Time",
            f"{total_duration:.0f} min",
            delta=None
        )

    st.markdown("---")

    # Format data for display
    display_df = filtered_df.copy()
    # Format date for display - handle both datetime and date objects
    if hasattr(display_df['workout_date'].iloc[0], 'strftime'):
        display_df['Date'] = display_df['workout_date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    else:
        display_df['Date'] = display_df['workout_date'].astype(str)
    display_df['Activity'] = display_df['activity_type']
    display_df['Calories'] = display_df['kcal_burned'].astype(int)
    display_df['Distance (mi)'] = display_df['distance_mi'].round(2)
    display_df['Duration (min)'] = display_df['duration_min']
    display_df['Avg Pace'] = display_df['avg_pace']
    display_df['Steps'] = display_df['steps'].fillna(0).astype(int)
    
    # Select columns for display
    columns_to_show = ['Date', 'Activity', 'Calories', 'Distance (mi)', 
                       'Duration (min)', 'Avg Pace', 'Steps']
    
    st.dataframe(
        display_df[columns_to_show],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Calories": st.column_config.NumberColumn(
                "Calories",
                help="Calories burned during workout",
                format="%d"
            ),
            "Distance (mi)": st.column_config.NumberColumn(
                "Distance (mi)",
                help="Distance covered in miles",
                format="%.2f"
            ),
            "Duration (min)": st.column_config.NumberColumn(
                "Duration (min)",
                help="Workout duration in minutes",
                format="%.1f"
            ),
            "Steps": st.column_config.NumberColumn(
                "Steps",
                help="Steps taken during workout",
                format="%d"
            )
        }
    )

else:
    st.info("No workouts found matching your filter criteria.")

st.markdown("---")
st.caption(f"Showing {len(filtered_df)} of {len(df)} total workouts")