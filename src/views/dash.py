from utils.session_manager import SessionManager
from utils.utilities import calculate_workout_statistics, get_db_connection
from services.database_service import DatabaseService
from config.database import DatabaseConfig
from config.app import STYLE_CONFIG
import streamlit as st
from streamlit_calendar import calendar
from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import toml
import json
import os
from datetime import datetime, timedelta, date
import calendar as cl
import base64
from io import BytesIO
import platform

# Initialize SessionManager chrisedit
session_mgr = SessionManager()

GET_HELP = f"""
Dashboard 
... Monthly View
______ Metrics Cards for # workouts, distance (mi), duration (hrs), calories, Walks/Jogs
______ Calendar in month view with workouts written as events, e.g. "1.12 Interval Training, Run"
... Detailed Stats
______ Selector for which week, activity type 
             Bar Graph of Distance (mi) per day | Duration (H) per day | Kcal per day | # workouts per day
---
"""

# Setup session
# st.set_page_config(
#     page_title="Fitness Dashboard",
#     page_icon=":material/dashboard:",
#     layout="wide",
#     # initial_sidebar_state="collapsed",
#     menu_items={
#         "Get help": "https://www.streamlit.io/", 
#         "Report a bug": "mailto:dagny099@gmail.com", 
#         "About": GET_HELP},
# )

# ------ SIDEBAR ------ #
st.sidebar.subheader("Connect to Database 🛢️")

# Select connection type 
# 1. Determine environment
if platform.system() == "Darwin":
    ENV = "development"
    connection_type = st.sidebar.selectbox("Select Connection Type", ["Local", "Remote"], index=0)
else:
    ENV = "production"
    connection_type = st.sidebar.selectbox("Select Connection Type", ["Local", "Remote"], index=1)

# Load db config from .streamlit/secrets.toml
if connection_type == "Local":
    dbconfig = {
        "host": "localhost",  # or your local DB host
        "port": 3306,         # default MySQL port
        "username": os.environ.get("MYSQL_USER"),
        "password": os.environ.get("MYSQL_PWD")
}
else:
    dbconfig = {
        "host": os.getenv("RDS_ENDPOINT"),
        "port": 3306,
        "username": os.getenv("RDS_USER"),
        "password": os.getenv("RDS_PASSWORD")
    }
dbconfig['database'] = "sweat"  # Database name

# ----------- DATA ----- #
# Load data once at the beginning of the session
@st.cache_data
def load_data():
    """Load the workout data once and cache it"""
    tmpMsg = st.sidebar.empty()
    tmpMsg.write("Connecting to MySQL database...")

    # Connect to the database
    conn = get_db_connection(dbconfig=dbconfig)  
    tmpMsg.write("Connected to MySQL database!")

    # Load data from the database
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM workout_summary;")
            rows = cursor.fetchall()

        # Get column names
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]

        # Convert to DataFrame for display
        df = pd.DataFrame(rows, columns=columns)

    except Exception as e:
        tmpMsg.error(f"Error executing query, 'SELECT * FROM workout_summary': {str(e)}")
    else:
        tmpMsg.info("Execute a query to see results here.")

    # **** RETURN HERE TO RECATEGORIZE DYAMICALLY
    df["color"] = df["distance_mi"].apply(assign_color)
    df["start"] = df["workout_date"].apply(lambda x: x.isoformat())
    df["end"] = df["start"]
    df["title"] = df["link"]      
    df['workout_date'] = pd.to_datetime(df['workout_date'])
    return df

# REPLACE THIS WITH A REAL CATEGOROZATION ALGO
def assign_color(criteria):
    if criteria > 5:
        return "#1f77b4"  # Blue
    elif (criteria >= 2) & (criteria < 5):
        return "#ff7f0e"  # Orange
    else:
        return "#888888"  # Default gray

# SHOW NICE METRICS CARDS
def display_workout_statistics(df_sub):
    """
    Display workout statistics in aesthetically pleasing cards.
    
    Parameters:
    -----------
    df_sub : pandas.DataFrame
        DataFrame containing workout data
    """
    # Calculate statistics
    stats = calculate_workout_statistics(df_sub)
    
    # Define friendly display names and units
    display_config = {
        'distance_mi': {'name': 'Distance', 'unit': 'miles', 'icon': '🏃', 'color': '#3498db'},
        'duration_sec': {'name': 'Duration', 'unit': '', 'icon': '⏱️', 'color': '#2ecc71'},
        'kcal_burned': {'name': 'Calories', 'unit': 'kcal', 'icon': '🔥', 'color': '#e74c3c'},
        'max_pace': {'name': 'Max Pace', 'unit': 'min/mi', 'icon': '⚡', 'color': '#f39c12'},
        'steps': {'name': 'Steps', 'unit': '', 'icon': '👣', 'color': '#9b59b6'}
    }
    
    # Custom CSS for cards
    st.markdown("""
    <style>
    .metric-card {
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .metric-value {
        font-size: 1rem;
        margin-bottom: 5px;
    }
    .center-text {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create layout with columns
    cols = st.columns(len(display_config))
    
    # Display cards for each metric
    for i, (col_name, config) in enumerate(display_config.items()):
        with cols[i]:
            # Format values appropriately
            if col_name == 'duration_sec':
                avg_value = str(timedelta(seconds=int(stats[col_name]['avg']))) if not np.isnan(stats[col_name]['avg']) else "N/A"
                median_value = str(timedelta(seconds=int(stats[col_name]['median']))) if not np.isnan(stats[col_name]['median']) else "N/A"
                std_value = str(timedelta(seconds=int(stats[col_name]['std']))) if not np.isnan(stats[col_name]['std']) else "N/A"
            else:
                avg_value = f"{stats[col_name]['avg']:.2f} {config['unit']}" if not np.isnan(stats[col_name]['avg']) else "N/A"
                median_value = f"{stats[col_name]['median']:.2f} {config['unit']}" if not np.isnan(stats[col_name]['median']) else "N/A"
                std_value = f"{stats[col_name]['std']:.2f} {config['unit']}" if not np.isnan(stats[col_name]['std']) else "N/A"
            
            # Create card
            st.markdown(f"""
            <div class="metric-card" style="background-color: {config['color']}20;">
                <div class="center-text">
                    <div class="metric-icon">{config['icon']}</div>
                    <div class="metric-title">{config['name']}</div>
                    <div class="metric-value"><strong>Count:</strong> {stats[col_name]['count']}</div>
                    <div class="metric-value"><strong>Average:</strong> {avg_value}</div>
                    <div class="metric-value"><strong>Median:</strong> {median_value}</div>
                    <div class="metric-value"><strong>Std Dev:</strong> {std_value}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def create_calendar_events(df):
    """Create properly formatted calendar events from DataFrame"""
    events = []
    for idx, row in df.iterrows():
        try:
            # Format the date correctly
            start_date = row['workout_date'].isoformat()
            
            # Create informative title
            title = f"{row['distance_mi']:.1f}mi {row['activity_type']}"
            
            events.append({
                "title": title,
                "start": start_date,
                "end": start_date,
                "color": row["color"]
            })
        except Exception as e:
            # Skip problematic rows
            continue
    return events

def get_week_dates(year, month, week_num):
    # Convert week_num to integer if it's a string
    if isinstance(week_num, str):
        try:
            week_num = int(week_num)
        except ValueError:
            # If conversion fails, default to week 1
            week_num = 1
    
    # Get the calendar for the given month and year
    month_calendar = cl.monthcalendar(year, month)

    # Get the start date of the week
    if week_num == 1 and month_calendar[0][0] == 0: # Week starts from the previous month
        start_date = datetime(year, month, 1)
    else:
        start_date = datetime(year, month, month_calendar[week_num-1][0])

    # Get the end date of the week
    end_date = start_date + timedelta(days=6)

    return start_date.date(), end_date.date()


# ============================================= #
# Initialize the app state
if 'full_data' not in st.session_state:
    # Load data only once
    st.session_state.full_data = load_data()
    
if 'filtered_data' not in st.session_state:
    # Initially, filtered data is the same as full data
    st.session_state.filtered_data = st.session_state.full_data.copy()

if 'calendar_start_date' not in st.session_state:
    st.session_state.calendar_start_date = None
    
if 'calendar_end_date' not in st.session_state:
    st.session_state.calendar_end_date = None

# ---------- STYLING --------------------- #
# 0. ADD DASHBORD STYLING HERE
with open("src/style_config.json") as config_file:
    style_config = json.load(config_file)
# ONCE SELTTLED, MOVE THIS INTO CSS FILE ABOVE
st.markdown(
    """
    <style>
    .metric-container {
        border: 1px solid #d1d1d1;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        text-align: center;
        background-color: #f9f9f9;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Extract color and font styles from configuration
colors, font = style_config['colors'], style_config['font']

    
# ------ Dashboard Layout: Main Window ------ #
st.title("Fitness Dashboard")

# ---------------------
# STEP 1: Date Picker
# ---------------------
c1, c2, c3 = st.columns([2, 1, 1])
# with c1:
#     st.markdown("#### 📆 Select a Month to View Your Calendar: ")
with c2:
    selected_date = st.date_input("PICK ANY DATE IN THE MONTH you're interested in", value=date(2025, 4, 20)) #, label_visibility="collapsed")


# ---------------------
# STEP 2: Calculate month range
# ---------------------
month_start = selected_date.replace(day=1)
_, last_day = cl.monthrange(month_start.year, month_start.month)
month_end = month_start.replace(day=last_day)
selected_month_top = month_start.strftime("%B")   # e.g., "April"
selected_year_top = month_start.year                   # e.g., 2025
with c1:
    st.markdown(f"### 📅 Showing calendar for **{selected_month_top} {selected_year_top}**")

# ---------------------
# STEP 3: Filter by selected month
# ---------------------
st.session_state.filtered_data = st.session_state.full_data[
    (st.session_state.full_data['workout_date'] >= datetime.combine(month_start, datetime.min.time())) & 
    (st.session_state.full_data['workout_date'] < datetime.combine(month_end, datetime.max.time()))
]

# ---------------------
# STEP 4: Format calendar events
# ---------------------
events = create_calendar_events(st.session_state.filtered_data)

# ---------------------
# STEP 5: Render the calendar
# ---------------------
calendar_options = {
    "initialView": "dayGridMonth",
    "initialDate": month_start.isoformat(),
    "editable": False,
    "selectable": False,  # Allows date range selection
    "navLinks": False,
    "headerToolbar": {
        "left": None,
        "center": "title",
    },
}

with st.expander(f"METRICS for **{selected_month_top} {selected_year_top}**", expanded=True, icon=':material/insights:'):
    display_workout_statistics(st.session_state.filtered_data)

stats = calculate_workout_statistics(st.session_state.filtered_data)

# Create tabs
dashboard_tab, details_tab = st.tabs([
    "MONTHLY VIEW", 
    "DETAILED STATS"
])

# Tab 1: Current Query and Response
with dashboard_tab:

    # SHOW CALENDAR
    
    calendar_result = calendar(
        events=events,
        options=calendar_options,
        custom_css= """
            .fc .fc-daygrid-event {
                background-color: #1f77b4;
                color: white;
                border: none;
            }
        """,
        key=f"calendar_{month_start.isoformat()}"  # 👈 dynamic key triggers re-render
    )


# Tab 2: DETAILED STATS
with details_tab:
    st.header("🏋️‍♀️ Weekly Workout Breakdown")

    col1, col2, col3 = st.columns(3)

    # Year Selector
    df = st.session_state.full_data
    # 1. Year Selector
    years = sorted(df["workout_date"].dt.year.unique())
    years = [str(year) for year in years]
    try:
        default_year_index = years.index(str(month_start.year))
    except ValueError:
        default_year_index = len(years) - 1 if years else 0
    detail_selected_year = col1.selectbox("Select Year", options=years, index=default_year_index)
    # Convert to integer for filtering (handle None case)
    if detail_selected_year is None:
        detail_selected_year = datetime.now().year  # Default to current year
    else:
        detail_selected_year = int(detail_selected_year)

    # 2. Month Selector
    months = sorted(df[df["workout_date"].dt.year == detail_selected_year]["workout_date"].dt.month.unique())
    months = [str(month) for month in months]
    try:
        default_month_index = months.index(str(month_start.month))
    except ValueError:
        default_month_index = len(months) - 1 if months else 0
    selected_month_idx = col2.selectbox("Select Month", options=months, index=default_month_index)
    detail_selected_month = months.index(selected_month_idx) 
    
    # 3. Filter by year & month
    month_df = df[
        (df["workout_date"].dt.year == detail_selected_year) &
        (df["workout_date"].dt.month == detail_selected_month + 1)
    ].copy()
    month_df["week_number"] = (month_df["workout_date"].dt.day - 1) // 7 + 1


    # 4. Week Selector with "All"
    week_options = ["All"] + sorted(month_df["week_number"].unique().tolist())
    selected_week = col3.selectbox("Select Week", week_options)

    if selected_week != "All":
        start_date, end_date = get_week_dates(detail_selected_year, detail_selected_month + 1, selected_week)    
        st.write(f"The dates for Week {selected_week} of {cl.month_name[detail_selected_month+1]} {detail_selected_year} are from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    else:
        start_date, _ =  get_week_dates(detail_selected_year, detail_selected_month + 1, 1)    
        _, end_date =  get_week_dates(detail_selected_year, detail_selected_month + 1, week_options[-1])    
        st.write(f"The dates for ALL of {cl.month_name[detail_selected_month+1]} {detail_selected_year} go from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")


    # 5. Activity Type Selector
    activity_types = ["All - Jogs, Races, Dog walks"] # df["activity_type"].unique().tolist()
    selected_activities = st.multiselect("Select Activity Type(s)", activity_types, default=activity_types)


    # ---------------------
    # *** Apply Filtering by selected period ***
    # ---------------------
    # if st.session_state.get("filtered_data_detail") is None:
    #     st.session_state.filtered_data_detail = month_df.copy()
    
    # Filter by selected week
    if selected_week != "All":
        filtered_df = month_df[month_df["week_number"] == selected_week].copy()
    else:
        filtered_df = month_df.copy()

    # Add Activity Type Filter back later, when activity_types are real
    # filtered_df = filtered_df[filtered_df["activity_type"].isin(selected_activities)]  

    # 6. Add day of week info
    day_names = pd.Categorical(
        filtered_df["workout_date"].dt.day_name(),
        categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        ordered=True
    )
    week_starts = filtered_df["workout_date"] - pd.to_timedelta(filtered_df["workout_date"].dt.weekday, unit="d")
    dur_min = filtered_df['duration_sec']/60

    filtered_df["day_of_week"] = day_names
    filtered_df["week_start"] = week_starts   
    filtered_df["duration_min"] = dur_min

    st.session_state.filtered_data_detail = filtered_df

    # ---------------------------
    # Display the calendar with the selected month and year
    with st.expander(f"METRICS for **{cl.month_name[detail_selected_month+1]} {detail_selected_year}**", expanded=True, icon=':material/insights:'):
        display_workout_statistics(st.session_state.filtered_data_detail)


    # (Optional) Display Data
    with st.expander("Filtered Data:", expanded=False, icon="📊"):
        if selected_week == "All":
            st.markdown(f"#### Aggregated for **All Weeks in {cl.month_name[detail_selected_month+1]} {detail_selected_year}**")
        else:
            st.markdown(f"#### Week {selected_week} of {cl.month_name[detail_selected_month+1]} {detail_selected_year}, from {start_date} to {end_date}")
        st.dataframe(st.session_state.filtered_data_detail)
    


#     # ---------------------------
#     spark = go.Figure(go.Scatter(
#         y=filtered_df["distance_mi"],
#         mode="lines+markers",
#         line=dict(color="#1f77b4", width=2),
#         marker=dict(size=3)
#     ))
#     spark.update_layout(
#         margin=dict(l=0, r=0, t=0, b=0),
#         height=60,
#         width=250,
#         xaxis=dict(visible=False),
#         yaxis=dict(visible=False)
#     )
#     st.plotly_chart(spark)


#     # ---------------------------


    # ==========================
    # GRAPH 1: Count workouts per day
    # ==========================
    workout_counts = (
        filtered_df["day_of_week"]
        .value_counts()
        .reindex(filtered_df["day_of_week"].cat.categories)
        .rename_axis("day_of_week")
        .reset_index(name="workout_count")
    )

    #Compute average for reference line
    avg_workouts = workout_counts["workout_count"].mean()
    
    # Identify Y-axis max to prevent cutoff
    y_max = workout_counts["workout_count"].max()

    #............. SCATTER VERSION ............. 
    fig_scatter = px.scatter(
        workout_counts,
        x="day_of_week",
        y="workout_count",
        size="workout_count",
        color_discrete_sequence=["#1f77b4"],  # consistent color
        text="workout_count",
        title="🏋️‍♀️ Total Workouts per Day of Week (Scatter)",
        labels={"day_of_week": "Day", "workout_count": "# Workouts"},
    )

    fig_scatter.update_traces(
        marker=dict(opacity=0.8),
        textposition="top center"
    )

    fig_scatter.add_hline(
        y=workout_counts["workout_count"].mean(),
        line_dash="dash",
        line_color="gray",
        annotation_text="Average",
        annotation_position="top left"
    )

    fig_scatter.update_layout(
        yaxis=dict(
            title="# of Workouts",
            tickformat=".0f",
            range=[0, y_max + 1]
        ),
        xaxis_title="Day of Week",
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig_scatter, use_container_width=True)
    
    #............... LOLLIPOP VERSION without sticks ...............
    fig_lollipop1 = go.Figure()

    # Stem lines
    fig_lollipop1.add_trace(go.Scatter(
        x=workout_counts["day_of_week"],
        y=workout_counts["workout_count"],
        mode='lines',
        line=dict(color='gray', width=2),
        hoverinfo='skip',
        showlegend=False
    ))

    # Circle markers
    fig_lollipop1.add_trace(go.Scatter(
        x=workout_counts["day_of_week"],
        y=workout_counts["workout_count"],
        mode='markers+text',
        marker=dict(size=12, color="#1f77b4"),
        text=workout_counts["workout_count"],
        textposition="top center",
        name="# Workouts"
    ))

    # Reference line
    fig_lollipop1.add_hline(
        y=workout_counts["workout_count"].mean(),
        line_dash="dash",
        line_color="gray",
        annotation_text="Average",
        annotation_position="top left"
    )

    fig_lollipop1.update_layout(
        title="🏋️‍♀️ Total Workouts per Day of Week (Lollipop)",
        xaxis_title="Day of Week",
        yaxis_title="# of Workouts",
        yaxis=dict(tickformat=".0f", range=[0, y_max + 1]),
        height=400
    )

    st.plotly_chart(fig_lollipop1, use_container_width=True)

    #............... LOLLIPOP VERSION 2 ...............
    fig_lollipop = go.Figure()

    # Add vertical stems (one per day)
    for i, row in workout_counts.iterrows():
        fig_lollipop.add_trace(go.Scatter(
            x=[row["day_of_week"], row["day_of_week"]],
            y=[0, row["workout_count"]],
            mode="lines",
            line=dict(color="gray", width=2),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add circle markers
    fig_lollipop.add_trace(go.Scatter(
        x=workout_counts["day_of_week"],
        y=workout_counts["workout_count"],
        mode="markers+text",
        marker=dict(size=12, color="#1f77b4"),
        text=workout_counts["workout_count"],
        textposition="top center",
        name="# Workouts"
    ))

    # Add average reference line
    fig_lollipop.add_hline(
        y=workout_counts["workout_count"].mean(),
        line_dash="dash",
        line_color="gray",
        annotation_text="Average",
        annotation_position="top left"
    )

    fig_lollipop.update_layout(
        title="🏋️‍♀️ Total Workouts per Day of Week (Lollipop Style)",
        xaxis_title="Day of Week",
        yaxis_title="# of Workouts",
        yaxis=dict(tickformat=".0f", range=[0, y_max + 1]),
        height=400
    )

    st.plotly_chart(fig_lollipop, use_container_width=True)


    # ==========================
    # GRAPH 2: Count workouts per day
    # ==========================

    # ---- STEP 1: Ensure datetime format and derive week start ----
    # filtered_df["workout_date"] = pd.to_datetime(filtered_df["workout_date"])
    # filtered_df["week_start"] = filtered_df["workout_date"] - pd.to_timedelta(filtered_df["workout_date"].dt.weekday, unit="d")

    # ---- STEP 2: Aggregate weekly distance ----
    weekly_distance = filtered_df.groupby("week_start")["distance_mi"].sum().reset_index()
    weekly_distance = weekly_distance.sort_values("week_start")

    # ---- STEP 3: Calculate average for reference line ----
    avg_distance = weekly_distance["distance_mi"].mean()
    y_max = weekly_distance["distance_mi"].max()

    # ---- STEP 4: Build the bar chart ----
    fig_distance = go.Figure()

    # Bars
    fig_distance.add_trace(go.Bar(
        x=weekly_distance["week_start"],
        y=weekly_distance["distance_mi"],
        marker_color="#17BECF",
        text=weekly_distance["distance_mi"].round(2),
        textposition="outside",
        name="Weekly Distance",
        hovertemplate="Week of %{x|%b %d, %Y}<br>Distance: %{y:.2f} mi<extra></extra>"
    ))

    # Reference line: average
    fig_distance.add_hline(
        y=avg_distance,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Avg: {avg_distance:.1f} mi",
        annotation_position="top left"
    )

    # ---- STEP 5: Layout tweaks ----
    fig_distance.update_layout(
        title="📏 Total Distance Week of the Month",
        xaxis_title="Week Start",
        yaxis_title="Distance (miles)",
        yaxis=dict(
            tickformat=".0f",
            range=[0, y_max + 1]
        ),
        bargap=0.2,
        height=400
    )

    st.plotly_chart(fig_distance, use_container_width=True)

    #............... AREA CHART VERSION ...............
    fig_area = px.area(
        weekly_distance,
        x="week_start",
        y="distance_mi",
        title="📈 Weekly Distance Trend (Area Chart)",
        labels={"week_start": "Week Start", "distance_mi": "Distance (mi)"},
        color_discrete_sequence=["#17BECF"]
    )

    fig_area.add_hline(
        y=avg_distance,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Avg: {avg_distance:.1f} mi",
        annotation_position="top left"
    )

    fig_area.update_traces(mode="lines+markers", hovertemplate="Week of %{x|%b %d, %Y}<br>Distance: %{y:.2f} mi<extra></extra>")
    fig_area.update_layout(
        yaxis=dict(tickformat=".0f", range=[0, y_max + 1]),
        xaxis_title="Week Start",
        yaxis_title="Distance (miles)",
        height=400
    )

    st.plotly_chart(fig_area, use_container_width=True)


    # ==========================
    # GRAPH 3: DURATION PER WEEK
    # ==========================

    #............... BAR CHART VERSION ...............
    # STEP 1: Ensure datetime and calculate week start
    # filtered_df["workout_date"] = pd.to_datetime(df["workout_date"])
    # filtered_df["week_start"] = filtered_df["workout_date"] - pd.to_timedelta(filtered_df["workout_date"].dt.weekday, unit="d")

    # filtered_df["duration_min"] = filtered_df['duration_sec']/60

    # filtered_df["day_of_week"] = pd.Categorical(
    #     filtered_df["workout_date"].dt.day_name(),
    #     categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    #     ordered=True
    # )

    # STEP 2: Aggregate total duration per week
    weekly_duration = filtered_df.groupby("week_start")["duration_min"].sum().reset_index()
    weekly_duration = weekly_duration.sort_values("week_start")
    avg_duration = weekly_duration["duration_min"].mean()
    y_max = weekly_duration["duration_min"].max()

    # STEP 3: Bar chart (total duration)

    fig_duration_sum = go.Figure()

    fig_duration_sum.add_trace(go.Bar(
        x=weekly_duration["week_start"],
        y=weekly_duration["duration_min"],
        marker_color="#9467bd",
        text=weekly_duration["duration_min"].round(1),
        textposition="outside",
        name="Total Duration",
        hovertemplate="Week of %{x|%b %d, %Y}<br>Total Duration: %{y:.1f} min<extra></extra>"
    ))

    fig_duration_sum.add_hline(
        y=avg_duration,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Avg: {avg_duration:.1f} min",
        annotation_position="top left"
    )

    fig_duration_sum.update_layout(
        title="⏱️ Total Duration per Week",
        xaxis_title="Week Start",
        yaxis_title="Duration (minutes)",
        yaxis=dict(tickformat=".0f", range=[0, 700]),
        bargap=0.2,
        height=400
    )

    st.plotly_chart(fig_duration_sum, use_container_width=True)


    #............... BOX PLOT VERSION ...............

    fig_duration_box = px.box(
        filtered_df,
        x="day_of_week",
        y="duration_min",
        color_discrete_sequence=["#9467bd"],
        title="⏳ Duration Distribution per Day of Week",
        labels={"day_of_week": "Day", "duration_min": "Duration (minutes)"}
    )

    fig_duration_box.update_traces(
        jitter=0.3,
        marker=dict(opacity=0.5, size=6),
        line=dict(width=1)
    )

    fig_duration_box.update_layout(
        yaxis=dict(tickformat=".0f", range=[0, 1000]),
        height=400
    )

    st.plotly_chart(fig_duration_box, use_container_width=True)


    # # ==========================
    # # ==========================
    # # Chart 1: Number of Workouts per Day
    # count_df = filtered_df["day_of_week"].value_counts().rename_axis("day_of_week").reset_index(name="workout_count")
    # count_df = count_df.sort_values("day_of_week", key=lambda x: pd.Categorical(x, categories=[
    #     "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    # ], ordered=True))

    # fig1 = px.bar(
    #     count_df,
    #     x="day_of_week",
    #     y="workout_count",
    #     title="📊 Number of Workouts per Day of Week",
    #     labels={"day_of_week": "Day of Week", "workout_count": "# Workouts"},
    #     color="day_of_week",
    # )

    # fig1.update_layout(
    #     xaxis_title="Day of Week",
    #     yaxis_title="# Workouts",
    #     yaxis=dict(tickformat=".0f")  # force integer ticks
    # )

    # # Optional: interactive click handling (see below)
    # # st.plotly_chart(fig1, use_container_width=True)
    # click_data = plotly_events(
    #     fig1,
    #     click_event=True,
    #     hover_event=False,
    #     select_event=False,
    #     override_height=400
    # )
    # if click_data:
    #     clicked_day = click_data[0]['x']
    #     st.markdown(f"### 📋 Workouts on {clicked_day}")
    #     clicked_workouts = filtered_df[filtered_df["day_of_week"] == clicked_day]
    #     st.dataframe(clicked_workouts[["workout_date", "activity_type", "distance_mi"]])


    # # Chart 2: Average Distance per Day
    # avg_df = filtered_df.groupby("day_of_week")["distance_mi"].mean().reset_index()
    # avg_df["distance_mi"] = avg_df["distance_mi"].round(2)
    # avg_df = avg_df.sort_values("day_of_week", key=lambda x: pd.Categorical(x, categories=[
    #     "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    # ], ordered=True))

    # fig2 = px.bar(
    #     avg_df,
    #     x="day_of_week",
    #     y="distance_mi",
    #     title="📏 Average Distance (mi) per Day of Week",
    #     labels={"day_of_week": "Day of Week", "distance_mi": "Avg Distance (mi)"},
    #     color="day_of_week"
    # )

    # fig2.update_layout(
    #     xaxis_title="Day of Week",
    #     yaxis_title="Average Distance (mi)",
    #     yaxis=dict(tickformat=".0f") if avg_df["distance_mi"].max() > 3 else dict(tickformat=".2f")
    # )
    # st.plotly_chart(fig2, use_container_width=True)

    # # ==========================
    # # ==========================
    # # 9. Bar Chart: # Workouts per Day
    # workout_counts = filtered_df["day_of_week"].value_counts().sort_index()
    # st.bar_chart(workout_counts)

    # # 10. Bar Chart: Avg Distance per Day
    # avg_distance = filtered_df.groupby("day_of_week")["distance_mi"].mean().sort_index()
    # st.bar_chart(avg_distance)

    # # ==========================
    # # ==========================
    # st.markdown("### DETAILED STATS")
    # Display results
    # st.subheader("Stats returned from function")
    # st.dataframe(stats)
    # total_workouts = 
    # avg_distance = 
    # avg_duration = 
    # avg_calories = 
    # fastest_speed = 
    # metrics = [
    #     {"label": "Total Workouts", "value": total_workouts, "color": colors["distance"]},
    #     {"label": "Avg Distance", "value": f"{avg_distance} km", "color": colors["distance"]},
    #     {"label": "Avg Duration", "value": f"{avg_duration} min", "color": colors["duration"]},
    #     {"label": "Avg Calories", "value": f"{avg_calories} kcal", "color": colors["calories"]},
    #     {"label": "Fastest Speed", "value": f"{fastest_speed} km/h", "color": colors["speed"]},
    # ]

    # # Display metrics in columns
    # col1, col2, col3 = st.columns(3)

    # with col1:
    #     st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    #     st.metric(label=metrics[0]['label'], value=metrics[0]['value'])
    #     st.markdown('</div>', unsafe_allow_html=True)

    # with col2:
    #     st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    #     st.metric(label=metrics[2]['label'], value=metrics[2]['value'])
    #     st.metric(label=metrics[3]['label'], value=metrics[3]['value'])
    #     st.markdown('</div>', unsafe_allow_html=True)

    # with col3:
    #     st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    #     st.metric(label=metrics[4]['label'], value=metrics[4]['value'])
    #     st.markdown('</div>', unsafe_allow_html=True)

# # Trend Analysis Section
# st.subheader("Trend Analysis")
# metric_choice = st.selectbox("Select a metric to view trend:", ["Distance", "Duration", "Calories", "Speed"])

# # Time series visualization
# df['workout_date'] = pd.to_datetime(df['workout_date'])
# df['num_workouts'] = df.groupby('workout_date')['workout_id'].transform('count')

# y_metric = 'avg_pace'
# fig = px.line(
#     df,
#     x="workout_date",
#     y=y_metric,
#     title=f"Time Series of {y_metric.replace('_', ' ').title()}",
#     labels={"workout_date": "Date", y_metric: y_metric.replace('_', ' ').title()},
#     markers=True
# )

# st.plotly_chart(fig)

# # Footer spacing
# st.markdown("<div style='padding: 20px'></div>", unsafe_allow_html=True)