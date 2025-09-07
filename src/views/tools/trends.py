import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.database_service import DatabaseService

st.markdown("# 📈 Fitness Trends")
st.markdown("*Discover patterns and track your progress over time*")

@st.cache_data
def load_workout_data():
    """Load workout data from database for trends analysis"""
    try:
        db_service = DatabaseService()
        
        query = """
        SELECT workout_date, activity_type, kcal_burned, distance_mi, 
               duration_sec, avg_pace, steps
        FROM workout_summary 
        ORDER BY workout_date DESC
        """
        
        with db_service.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            
            if rows:
                df = pd.DataFrame(rows)
                df['duration_min'] = (df['duration_sec'] / 60).round(1)
                # Add derived columns for trend analysis
                df['year_month'] = df['workout_date'].dt.to_period('M')
                df['week'] = df['workout_date'].dt.to_period('W')
                df['year'] = df['workout_date'].dt.year
                df['month'] = df['workout_date'].dt.month
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

# Time aggregation selector
time_period = st.sidebar.selectbox(
    "Time Period",
    ["Weekly", "Monthly"],
    index=1
)

# Apply filters
filtered_df = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
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

if filtered_df.empty:
    st.info("No workouts found matching your filter criteria.")
    st.stop()

# Summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_calories = filtered_df['kcal_burned'].mean()
    st.metric(
        "Avg Calories/Workout",
        f"{avg_calories:.0f}",
        delta=None
    )

with col2:
    total_workouts = len(filtered_df)
    days_span = (filtered_df['workout_date'].max() - filtered_df['workout_date'].min()).days + 1
    freq = total_workouts / (days_span / 7) if days_span > 0 else 0
    st.metric(
        "Workouts/Week",
        f"{freq:.1f}",
        delta=None
    )

with col3:
    avg_distance = filtered_df['distance_mi'].mean()
    st.metric(
        "Avg Distance",
        f"{avg_distance:.1f} mi",
        delta=None
    )

with col4:
    avg_duration = filtered_df['duration_min'].mean()
    st.metric(
        "Avg Duration",
        f"{avg_duration:.0f} min",
        delta=None
    )

st.markdown("---")

# Prepare data for visualizations
if time_period == "Monthly":
    period_col = 'year_month'
    trend_data = filtered_df.groupby(period_col).agg({
        'kcal_burned': 'mean',
        'distance_mi': 'mean',
        'duration_min': 'mean',
        'workout_date': 'count'
    }).reset_index()
    trend_data.columns = ['Period', 'Avg Calories', 'Avg Distance', 'Avg Duration', 'Workout Count']
else:  # Weekly
    period_col = 'week'
    trend_data = filtered_df.groupby(period_col).agg({
        'kcal_burned': 'mean',
        'distance_mi': 'mean', 
        'duration_min': 'mean',
        'workout_date': 'count'
    }).reset_index()
    trend_data.columns = ['Period', 'Avg Calories', 'Avg Distance', 'Avg Duration', 'Workout Count']

trend_data['Period_str'] = trend_data['Period'].astype(str)

# 1. Calories Burned Trend
st.subheader("🔥 Calories Burned Over Time")
if len(trend_data) > 1:
    calories_chart = alt.Chart(trend_data).mark_line(
        point=True,
        color='#ff6b6b'
    ).encode(
        x=alt.X('Period_str:O', title=f'{time_period} Period'),
        y=alt.Y('Avg Calories:Q', title='Average Calories'),
        tooltip=['Period_str', 'Avg Calories:Q', 'Workout Count:Q']
    ).properties(
        width=600,
        height=300
    )
    st.altair_chart(calories_chart, use_container_width=True)
else:
    st.info("Need more data points to show trends. Try adjusting your filters.")

st.markdown("---")

# 2. Workout Frequency
st.subheader("📅 Workout Frequency")
freq_chart = alt.Chart(trend_data).mark_bar(
    color='#4ecdc4'
).encode(
    x=alt.X('Period_str:O', title=f'{time_period} Period'),
    y=alt.Y('Workout Count:Q', title='Number of Workouts'),
    tooltip=['Period_str', 'Workout Count:Q']
).properties(
    width=600,
    height=300
)
st.altair_chart(freq_chart, use_container_width=True)

st.markdown("---")

# 3. Activity Type Distribution
st.subheader("🏃‍♀️ Activity Type Distribution")
activity_dist = filtered_df['activity_type'].value_counts().reset_index()
activity_dist.columns = ['Activity', 'Count']

col1, col2 = st.columns(2)

with col1:
    # Pie chart using Altair
    pie_chart = alt.Chart(activity_dist).mark_arc().encode(
        theta=alt.Theta('Count:Q'),
        color=alt.Color('Activity:N', scale=alt.Scale(scheme='category10')),
        tooltip=['Activity:N', 'Count:Q']
    ).properties(
        width=300,
        height=300
    )
    st.altair_chart(pie_chart)

with col2:
    # Display as metrics
    st.markdown("**Activity Breakdown:**")
    for _, row in activity_dist.iterrows():
        percentage = (row['Count'] / len(filtered_df)) * 100
        st.metric(
            row['Activity'],
            f"{row['Count']} workouts",
            f"{percentage:.1f}%"
        )

# 4. Distance Progress (for cardio activities)
cardio_activities = ['Run', 'Bike', 'Walk', 'Cycling']
cardio_data = filtered_df[filtered_df['activity_type'].isin(cardio_activities)]

if not cardio_data.empty and len(cardio_data) > 1:
    st.markdown("---")
    st.subheader("🏃 Distance Progress (Cardio Activities)")
    
    distance_trend = cardio_data.groupby(period_col).agg({
        'distance_mi': 'mean'
    }).reset_index()
    distance_trend['Period_str'] = distance_trend[period_col].astype(str)
    
    distance_chart = alt.Chart(distance_trend).mark_line(
        point=True,
        color='#45b7d1'
    ).encode(
        x=alt.X('Period_str:O', title=f'{time_period} Period'),
        y=alt.Y('distance_mi:Q', title='Average Distance (miles)'),
        tooltip=['Period_str', 'distance_mi:Q']
    ).properties(
        width=600,
        height=300
    )
    st.altair_chart(distance_chart, use_container_width=True)

# 5. Performance Insights
st.markdown("---")
st.subheader("💡 Key Insights")

insights = []

# Calculate trends
if len(trend_data) >= 2:
    latest_calories = trend_data['Avg Calories'].iloc[-1]
    previous_calories = trend_data['Avg Calories'].iloc[-2]
    calorie_change = ((latest_calories - previous_calories) / previous_calories) * 100
    
    if abs(calorie_change) > 5:
        direction = "increased" if calorie_change > 0 else "decreased"
        insights.append(f"🔥 Your average calorie burn has {direction} by {abs(calorie_change):.1f}% in the latest period")

# Workout frequency insight
avg_frequency = filtered_df.groupby(period_col).size().mean()
if time_period == "Monthly":
    if avg_frequency >= 8:
        insights.append("💪 Great consistency! You're averaging 2+ workouts per week")
    elif avg_frequency >= 4:
        insights.append("👍 Good consistency with 1+ workouts per week")
else:  # Weekly
    if avg_frequency >= 3:
        insights.append("🔥 Excellent! You're working out 3+ times per week")

# Activity diversity
unique_activities = len(filtered_df['activity_type'].unique())
if unique_activities >= 3:
    insights.append(f"🌟 Great variety! You're doing {unique_activities} different activity types")

# Display insights
if insights:
    for insight in insights:
        st.info(insight)
else:
    st.info("💭 Collect more workout data to see personalized insights!")

st.markdown("---")
st.caption(f"Analysis based on {len(filtered_df)} workouts in the selected period")