from utilities import execute_query, get_db_connection
from session_manager import SessionManager
import streamlit as st
import plotly.express as px
import pandas as pd
import toml
import json
import os
from datetime import datetime
import platform

# Initialize SessionManager chrisedit
session_mgr = SessionManager()

GET_HELP = f"""
Here's a quick guide to help you get started:
# TODO
---
"""

# ============================================= #
# Setup session
# st.set_page_config(
#     page_title="Fitness Dashboard",
#     page_icon="🐇",
#     layout="wide",
#     initial_sidebar_state="auto",
#     menu_items={
#         "Get help": "https://www.streamlit.io/", 
#         "Report a bug": "mailto:dagny099@gmail.com", 
#         "About": GET_HELP},
# )

# 0. Load dashboard style configuration from a JSON file
with open("src/style_config.json") as config_file:
    style_config = json.load(config_file)

# Custom CSS for styling
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
    .query-history {
        margin: 10px 0;
        padding: 10px;
        border-left: 3px solid #ccc;
    }
    .query-history:hover {
        border-left: 3px solid #0066cc;
        background-color: #f5f5f5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Extract color and font styles from configuration
colors, font = style_config['colors'], style_config['font']

# ------ Dashboard Layout: Sidebar ------ #
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

tmpMsg = st.sidebar.empty()
tmpMsg.write("Connecting to MySQL database...")
conn = get_db_connection(dbconfig=dbconfig)  # Connect to the database
tmpMsg.write("Connected to MySQL database!")

# Load data from the database
st.sidebar.subheader("Load Data to use for Visualization 📊")
if "subset_query" not in st.session_state:
    st.session_state["subset_query"] = "SELECT * FROM workout_summary LIMIT 6"

# Query table
subset_query = st.sidebar.text_area("Query table", value=st.session_state["subset_query"], max_chars=None)
st.session_state["subset_query"] = subset_query
response = execute_query(subset_query, dbconfig) 
df = pd.DataFrame(response)

st.sidebar.subheader("Session Scratchpad")
scratchpad_content = st.sidebar.text_area(
    "Notes",
    value=session_mgr.get_scratchpad(),
    height=150,
    placeholder="Use this space for notes, temporary queries, or any other session-related content..."
)
session_mgr.update_scratchpad(scratchpad_content)

# ------ Dashboard Layout: Main Window ------ #
st.title("Workout Dashboard")

# Query Editor Section with Tabs
st.subheader("SQL Query Editor")

# Create tabs
query_tab, history_tab, saved_tab = st.tabs([
    "Current Query", 
    "Query History", 
    "Saved Queries"
])

# Tab 1: Current Query and Response
with query_tab:
    # Create two columns for query input and results
    query_col, response_col = st.columns(2)
    
    # Query input column
    with query_col:
        st.markdown("### Query Input")
        query = st.text_area(
            "Enter your SQL query",
            placeholder="SELECT * FROM workout_summary",
            height=200,
            key="current_query"
        )
        
        # Add execution button with loading state
        execute_button = st.button(
            "Execute Query",
            type="primary",
            help="Run the SQL query"
        )
    
    # Response column
    with response_col:
        st.markdown("### Query Results")
        if execute_button and query:
            try:
                start_time = datetime.now()
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    # Get column names
                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        
                        # Convert to DataFrame for display
                        results_df = pd.DataFrame(rows, columns=columns)
                        
                        # Display execution metadata
                        st.success(f"Query executed successfully in {execution_time:.2f} seconds")
                        st.markdown(f"**Rows returned:** {len(rows)}")
                        
                        # Display results
                        st.dataframe(
                            results_df,
                            hide_index=True,
                            use_container_width=True
                        )
                        
                        # Add to session history
                        session_mgr.add_query_to_history(
                            query=query,
                            result={
                                'columns': columns,
                                'row_count': len(rows),
                                'execution_time': execution_time
                            }
                        )
                    else:
                        st.info("Query executed successfully, but no results were returned.")
                        
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")
                # Add failed query to history
                session_mgr.add_query_to_history(
                    query=query,
                    result={
                        'error': str(e),
                        'execution_time': (datetime.now() - start_time).total_seconds()
                    }
                )
        else:
            st.info("Execute a query to see results here.")

# Tab 2: Query History
with history_tab:
    st.markdown("### Recent Query History")
    
    # Get complete query history
    history = session_mgr.get_query_history()
    
    if not history:
        st.info("No query history available yet. Execute some queries to see them here!")
    else:
        # Add filter options
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search queries", "")
        with col2:
            show_only_successful = st.checkbox("Show only successful queries", True)
        
        # Filter history based on search and success status
        filtered_history = []
        for query_record in reversed(history):  # Show newest first
            query_text = query_record['query'].lower()
            is_successful = 'error' not in query_record.get('result', {})
            
            if search_term.lower() in query_text:
                if show_only_successful and is_successful:
                    filtered_history.append(query_record)
                elif not show_only_successful:
                    filtered_history.append(query_record)
        
        # Display filtered history
        for idx, record in enumerate(filtered_history):
            with st.expander(f"Query {len(history)-idx}: {record['query'][:50]}...", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.code(record['query'], language='sql')
                    st.caption(f"Executed at: {record['timestamp']}")
                    
                    # Show execution details
                    result = record.get('result', {})
                    if 'error' in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.success(f"Success - {result.get('row_count', 0)} rows returned")
                        if 'execution_time' in result:
                            st.caption(f"⚡ Execution time: {result['execution_time']:.2f}s")
                
                with col2:
                    # Add buttons for actions
                    if st.button("▶️ Run Again", key=f"rerun_{idx}"):
                        st.session_state.current_query = record['query']
                        st.experimental_rerun()
                    
                    if st.button("📌 Save Query", key=f"save_{idx}"):
                        session_mgr.add_saved_query(record['query'])
                        st.success("Query saved!")

# Tab 3: Saved Queries
with saved_tab:
    st.markdown("### Saved Queries")
    
    # Add a new query to saved queries
    with st.expander("➕ Add New Saved Query"):
        new_query_name = st.text_input("Query Name", placeholder="e.g., Monthly Workout Summary")
        new_query_text = st.text_area("SQL Query", placeholder="SELECT * FROM workout_summary")
        new_query_desc = st.text_area("Description (optional)", placeholder="Describe what this query does...")
        
        if st.button("Save Query"):
            if new_query_name and new_query_text:
                session_mgr.add_saved_query(
                    query=new_query_text,
                    name=new_query_name,
                    description=new_query_desc
                )
                st.success("Query saved successfully!")
            else:
                st.warning("Please provide both a name and query.")
    
    # Display saved queries
    saved_queries = session_mgr.get_saved_queries()
    
    if not saved_queries:
        st.info("No saved queries yet. Save some queries for quick access!")
    else:
        # Add search functionality
        search_saved = st.text_input("🔍 Search saved queries", "")
        
        # Filter and display saved queries
        for idx, saved_query in enumerate(saved_queries):
            if search_saved.lower() in saved_query['name'].lower() or \
               search_saved.lower() in saved_query['query'].lower():
                with st.expander(f"📌 {saved_query['name']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.code(saved_query['query'], language='sql')
                        if saved_query.get('description'):
                            st.markdown(f"*{saved_query['description']}*")
                    
                    with col2:
                        if st.button("▶️ Run", key=f"run_saved_{idx}"):
                            st.session_state.current_query = saved_query['query']
                            st.experimental_rerun()
                        
                        if st.button("🗑️ Delete", key=f"del_saved_{idx}"):
                            session_mgr.delete_saved_query(idx)
                            st.success("Query deleted!")
                            st.experimental_rerun()
                            

# Statistics Section
st.subheader("Statistics Calculated on Subset of Data")

total_workouts = df.shape[0]
avg_distance = round(df['distance_mi'].mean(), 2)
avg_duration = round(df['duration_sec'].mean(), 2)
avg_calories = round(df['kcal_burned'].mean(), 2)
fastest_speed = round(df['max_pace'].max(), 2)

metrics = [
    {"label": "Total Workouts", "value": total_workouts, "color": colors["distance"]},
    {"label": "Avg Distance", "value": f"{avg_distance} km", "color": colors["distance"]},
    {"label": "Avg Duration", "value": f"{avg_duration} min", "color": colors["duration"]},
    {"label": "Avg Calories", "value": f"{avg_calories} kcal", "color": colors["calories"]},
    {"label": "Fastest Speed", "value": f"{fastest_speed} km/h", "color": colors["speed"]},
]

# Display metrics in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric(label=metrics[0]['label'], value=metrics[0]['value'])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric(label=metrics[2]['label'], value=metrics[2]['value'])
    st.metric(label=metrics[3]['label'], value=metrics[3]['value'])
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric(label=metrics[4]['label'], value=metrics[4]['value'])
    st.markdown('</div>', unsafe_allow_html=True)

# Trend Analysis Section
st.subheader("Trend Analysis")
metric_choice = st.selectbox("Select a metric to view trend:", ["Distance", "Duration", "Calories", "Speed"])

# Time series visualization
df['workout_date'] = pd.to_datetime(df['workout_date'])
df['num_workouts'] = df.groupby('workout_date')['workout_id'].transform('count')

y_metric = 'avg_pace'
fig = px.line(
    df,
    x="workout_date",
    y=y_metric,
    title=f"Time Series of {y_metric.replace('_', ' ').title()}",
    labels={"workout_date": "Date", y_metric: y_metric.replace('_', ' ').title()},
    markers=True
)

st.plotly_chart(fig)

# Footer spacing
st.markdown("<div style='padding: 20px'></div>", unsafe_allow_html=True)

st.subheader("Workout Table")
st.dataframe(df, hide_index=True)

