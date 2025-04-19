"""
workout_dashboard.py

A modern, clean workout dashboard for fitness tracking using Streamlit.
This backbone focuses on layout and aesthetics, with modular styling
and component organization.

Usage:
    $ streamlit run workout_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import numpy as np

# ===== CONFIG AND STYLING ===== #

# Page Configuration
st.set_page_config(
    page_title="Personal Exercise Dashboard",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Color palette - centralized for easy theming with dark mode
COLORS = {
    "primary": "#68CBD0",    # Teal - main brand color
    "secondary": "#FF9D55",  # Orange - secondary accent
    "background": "#1e1e1e", # Dark gray - card background (dark mode)
    "app_bg": "#121212",     # Almost black - app background (dark mode)
    "text_primary": "#FFFFFF", # White - primary text (dark mode)
    "text_secondary": "#9e9e9e", # Light gray - secondary text (dark mode)
    "text_tertiary": "#666666", # Darker gray - tertiary text (dark mode)
    "progress_bg": "#333333", # Dark gray - progress background (dark mode)
    "chart_fill": "rgba(104, 203, 208, 0.2)", # Transparent teal for chart fill
    "border": "#333333"      # Border color for cards and elements
}

# Typography settings
TYPOGRAPHY = {
    "heading": "font-size: 2.5rem; font-weight: 700; color: #0e1117;",
    "subheading": "font-size: 1.5rem; font-weight: 600; color: #555;",
    "card_title": "font-size: 1.2rem; font-weight: 600; color: #555; margin-bottom: 1rem;",
    "metric_value": "font-size: 3.5rem; font-weight: 700; color: #0e1117; line-height: 1;",
    "metric_unit": "font-size: 1.8rem; color: #777; font-weight: 400;",
    "label_small": "font-size: 0.9rem; color: #777; margin-bottom: 0.2rem;"
}

# Modular CSS with all styling components
def load_css():
    """Load all CSS styles for the dashboard"""
    
    # Base styles - using dark theme to match screenshot
    base_styles = f"""
    /* Main container styling */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        background-color: #121212;
        color: white;
    }}
    
    /* Base app styling */
    .stApp {{
        background-color: #121212;
    }}
    
    /* Card containers */
    .metric-card {{
        background-color: #1e1e1e;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 100%;
    }}
    
    /* Metric value styling */
    .metric-value {{
        font-size: 3rem;
        font-weight: 700;
        color: white;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }}
    
    /* Metric label styling */
    .metric-label {{
        font-size: 1.2rem;
        font-weight: 500;
        color: #9e9e9e;
        margin-bottom: 10px;
    }}
    
    /* Units styling */
    .unit {{
        font-size: 1.5rem;
        color: #9e9e9e;
        font-weight: 400;
    }}
    
    /* Heading styling */
    h1, h2, h3, h4, h5, h6 {{
        color: white !important;
    }}
    
    /* Remove padding from containers */
    div[data-testid="stVerticalBlock"] {{
        gap: 0rem;
    }}
    """
    
    # Component styles
    component_styles = """
    /* Progress bar styling */
    .progress-container {
        height: 0.5rem;
        background-color: #eee;
        border-radius: 1rem;
        margin-top: 0.5rem;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 1rem;
    }
    
    /* Filter dropdowns */
    .filter-container {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Improve widget styling */
    div[data-testid="stVerticalBlock"] > div:has(div.stSelectbox) {
        background-color: white;
        border-radius: 10px;
        padding: 0px;
        margin-bottom: 1rem;
    }
    
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 0.5rem;
    }
    """
    
    # Load all CSS
    st.markdown(f"<style>{base_styles}{component_styles}</style>", unsafe_allow_html=True)

# Load the CSS
load_css()

# ===== DATA FUNCTIONS ===== #

def generate_sample_data(days=30):
    """
    Generate sample workout data for demonstration purposes.
    
    Args:
        days (int): Number of days of workout history to generate
        
    Returns:
        pandas.DataFrame: DataFrame with sample workout data
    """
    today = datetime.now()
    data = []
    
    for i in range(days):
        date = today - timedelta(days=i)
        # Skip some days randomly to simulate rest days
        if random.random() > 0.7 and i > 0:
            continue
            
        # Generate random workout data
        distance = round(random.uniform(3.0, 12.0), 1)
        duration_minutes = round(random.uniform(20, 90))
        calories = round(duration_minutes * random.uniform(8, 12))
        pace_seconds = round((duration_minutes * 60) / distance)
        pace_minutes = pace_seconds // 60
        pace_remain_seconds = pace_seconds % 60
        steps = round(distance * random.uniform(1000, 1300))
        
        data.append({
            'workout_date': date,
            'workout_type': 'Running',
            'distance_km': distance,
            'duration_min': duration_minutes,
            'kcal_burned': calories,
            'pace_min': pace_minutes,
            'pace_sec': pace_remain_seconds,
            'steps': steps,
            'avg_hr': round(random.uniform(140, 180)),
            'max_hr': round(random.uniform(170, 195))
        })
    
    return pd.DataFrame(data)

def load_data():
    """
    Load workout data from source (currently using sample data).
    In a production version, this would connect to your database.
    
    Returns:
        pandas.DataFrame: Workout data
    """
    # TODO: Replace with actual database connection code
    return generate_sample_data()

# ===== UI COMPONENT FUNCTIONS ===== #

def create_metric_card(title, value, unit=None, chart=None, icon=None, progress=None):
    """
    Create a metric card with consistent styling
    
    Args:
        title (str): Card title
        value (str/int/float): Main metric value to display
        unit (str, optional): Unit of measurement
        chart (dict, optional): Chart configuration
        icon (str, optional): HTML/SVG for icon
        progress (dict, optional): Progress indicator configuration
    """
    # Create a container for the card with custom styling
    card_container = st.container()
    
    # Apply card styling to the container
    with card_container:
        # Card wrapper with styling
        st.markdown("""
        <div style="background-color: #121212; border-radius: 15px; padding: 20px; margin-bottom: 15px; 
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1); height: 100%;">
        """, unsafe_allow_html=True)
        
        # Card title - inside the card at the top
        st.markdown(f"""
        <div style="font-size: 1.2rem; font-weight: 500; color: #9e9e9e; margin-bottom: 10px;">
            {title}
        </div>
        """, unsafe_allow_html=True)
        
        # Metric value with optional unit
        if unit:
            st.markdown(f"""
            <div style="font-size: 3rem; font-weight: 700; color: white; line-height: 1.2;">
                {value} <span style="font-size: 1.5rem; color: #9e9e9e;">{unit}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="font-size: 3rem; font-weight: 700; color: white; line-height: 1.2;">
                {value}
            </div>
            """, unsafe_allow_html=True)
    
    # Optional progress indicator
    if progress:
        if progress["type"] == "circle":
            # Circle progress indicator
            percentage = progress["percentage"]
            color = progress.get("color", COLORS["primary"])
            st.markdown(f"""
            <div style="margin-top: 1rem; width: 100px; height: 100px; position: relative; margin: 0 auto;">
                <div style="width: 100px; height: 100px; border-radius: 50%; background: {COLORS['progress_bg']}; position: absolute; top: 0; left: 0;"></div>
                <div style="width: 100px; height: 100px; border-radius: 50%; background: conic-gradient({color} 0% {percentage}%, {COLORS['progress_bg']} {percentage}% 100%); position: absolute; top: 0; left: 0;"></div>
                <div style="width: 70px; height: 70px; border-radius: 50%; background: white; position: absolute; top: 15px; left: 15px;"></div>
            </div>
            """, unsafe_allow_html=True)
        elif progress["type"] == "bar":
            # Linear progress bar
            percentage = progress["percentage"]
            color = progress.get("color", COLORS["primary"])
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {percentage}%; background-color: {color};"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                <span style="font-size: 0.8rem; color: {COLORS['text_light']};">{progress.get("left_label", "")}</span>
                <span style="font-size: 0.8rem; color: {COLORS['text_light']};">{progress.get("right_label", "")}</span>
            </div>
            """, unsafe_allow_html=True)
        elif progress["type"] == "goal":
            # Goal progress with icon
            percentage = progress["percentage"]
            color = progress.get("color", COLORS["secondary"])
            goal_text = progress.get("text", "Daily Goal")
            complete_text = progress.get("complete_text", f"{percentage}% Complete")
            
            st.markdown(f"""
            <div style="margin-top: 1rem; width: 100%; display: flex; align-items: center;">
                <div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(90deg, #FFD8B8 0%, {color} 75%); margin-right: 1rem;"></div>
                <div style="flex-grow: 1;">
                    <div style="font-size: 0.9rem; color: {COLORS['text_light']}; margin-bottom: 0.2rem;">{goal_text}</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: {COLORS['text_dark']};">{complete_text}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Optional icon
    if icon:
        st.markdown(f"""
        <div style="margin-top: 1rem; text-align: center;">
            {icon}
        </div>
        """, unsafe_allow_html=True)
        
    # Optional chart
    if chart:
        if chart["type"] == "line":
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=chart["x"], 
                y=chart["y"],
                mode='lines',
                line=dict(width=2, color=chart.get("color", COLORS["primary"])),
                fill='tozeroy',
                fillcolor=chart.get("fill_color", COLORS["chart_fill"])
            ))
            fig.update_layout(
                height=chart.get("height", 150),
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        elif chart["type"] == "bar":
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=chart["x"],
                y=chart["y"],
                marker_color=chart.get("color", COLORS["primary"]),
                width=chart.get("width", 0.6)
            ))
            fig.update_layout(
                height=chart.get("height", 230),
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False
                ),
                bargap=0.3
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_steps_icon():
    """Generate SVG icon for steps"""
    return """
    <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M19 5.5C19 6.88071 17.8807 8 16.5 8C15.1193 8 14 6.88071 14 5.5C14 4.11929 15.1193 3 16.5 3C17.8807 3 19 4.11929 19 5.5Z" fill="#E9EFF0"/>
        <path d="M13.3276 9.68601C13.614 9.93043 13.9081 10.2106 14.0768 10.5695C14.1443 10.7063 14.1871 10.845 14.1871 10.983C14.1871 11.121 14.1443 11.2598 14.0768 11.3965C13.9081 11.7554 13.614 12.0356 13.3276 12.28C12.0093 13.4151 10.6986 14.6113 9.34699 15.8285L7.33044 13.8963L7.36158 13.8658C8.76979 12.4945 10.1327 11.158 11.6038 9.88699C11.9279 9.60527 12.2642 9.33988 12.6386 9.16094C12.7807 9.0925 12.9276 9.0925 13.0697 9.16094C13.1604 9.20004 13.2465 9.24944 13.3276 9.30862" fill="#CBD5DA"/>
        <path d="M11.4743 14.4144C11.7607 14.6588 11.9956 15.0196 12.1643 15.3785C12.2318 15.5152 12.2746 15.6539 12.2746 15.792C12.2746 15.93 12.2318 16.0687 12.1643 16.2055C11.9956 16.5643 11.7607 16.9251 11.4743 17.1695C10.156 18.3046 8.8453 19.5008 7.49372 20.718L5.47717 18.7858L5.50831 18.7552C6.91652 17.384 8.27942 16.0475 9.75054 14.7765C10.0746 14.4947 10.4109 14.2293 10.7853 14.0504C10.9274 13.982 11.0743 13.982 11.2164 14.0504C11.3071 14.0895 11.3932 14.1389 11.4743 14.198" fill="#CBD5DA"/>
        <path d="M16.4697 12.5133C16.756 12.7577 16.9909 13.1186 17.1596 13.4774C17.2271 13.6141 17.2699 13.7528 17.2699 13.8909C17.2699 14.0289 17.2271 14.1677 17.1596 14.3044C16.9909 14.6632 16.756 15.0241 16.4697 15.2685C15.1513 16.4036 13.8406 17.5998 12.4891 18.817L10.4725 16.8848L10.5036 16.8542C11.9119 15.4829 13.2747 14.1464 14.7459 12.8754C15.0699 12.5937 15.4062 12.3283 15.7806 12.1493C15.9227 12.0809 16.0696 12.0809 16.2117 12.1493C16.3024 12.1884 16.3886 12.2378 16.4697 12.297" fill="#CBD5DA"/>
    </svg>
    """

# ===== DASHBOARD LAYOUT ===== #

def render_dashboard():
    """Main function to render the entire dashboard"""
    
    # Load data
    df = load_data()
    
    # ===== HEADER SECTION ===== #
    st.markdown("<h1 style='margin-bottom: 0.5rem;'>Personal Exercise Dashboard</h1>", unsafe_allow_html=True)

    # Filter dropdowns in the header - styled to match design
    col_filters1, col_filters2 = st.columns([1, 1])
    with col_filters1:
        # Custom container for the dropdown
        st.markdown("""
        <div style="background-color: white; border-radius: 10px; padding: 5px 15px; margin-bottom: 10px;">
        """, unsafe_allow_html=True)
        time_filter = st.selectbox("", ["Today", "This Week", "This Month", "Last 3 Months", "All Time"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_filters2:
        st.markdown("""
        <div style="background-color: white; border-radius: 10px; padding: 5px 15px; margin-bottom: 10px;">
        """, unsafe_allow_html=True)
        activity_filter = st.selectbox("", ["Running", "Cycling", "Swimming", "Walking", "All Activities"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    # ===== MAIN METRICS ROW ===== #
    # Create empty cards first to establish the grid layout
    st.markdown("""
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
        <div style="background-color: #1e1e1e; border-radius: 15px; padding: 20px; height: 350px;"> </div>
        <div style="background-color: #1e1e1e; border-radius: 15px; padding: 20px; height: 350px;"> </div>
        <div style="background-color: #1e1e1e; border-radius: 15px; padding: 20px; height: 350px;"> </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Now create the actual metric cards that will overlay on the grid
    col1, col2, col3 = st.columns(3)

    # Calories Burned Card
    with col1:
        # Sample line chart data
        calories_data = [{'x': i, 'y': random.randint(500, 850)} for i in range(10)]
        
        create_metric_card(
            title="Calories Burned",
            value="750",
            chart={
                "type": "line",
                "x": [d['x'] for d in calories_data],
                "y": [d['y'] for d in calories_data],
                "height": 100,
                "color": "#FF9D55" # Orange color for calories
            },
            progress={
                "type": "goal",
                "percentage": 75,
                "color": "#FF9D55" # Orange color for calories
            }
        )

    # Distance Card
    with col2:
        # Sample line chart data for distance
        distance_data = [{'x': i, 'y': random.uniform(5, 10)} for i in range(10)]
        
        create_metric_card(
            title="Distance Run",
            value="8,2",
            unit="km",
            chart={
                "type": "line",
                "x": [d['x'] for d in distance_data],
                "y": [d['y'] for d in distance_data],
                "height": 150,
                "color": "#68CBD0" # Teal color for distance
            }
        )

    # Duration Card
    with col3:
        create_metric_card(
            title="Workout Duration",
            value="1<span style='font-size: 1.5rem; color: #9e9e9e;'>h</span> 5<span style='font-size: 1.5rem; color: #9e9e9e;'>m</span>",
            progress={
                "type": "circle",
                "percentage": 75,
                "color": "#68CBD0" # Teal color for duration
            }
        )

    # ===== SECOND ROW WITH MORE METRICS ===== #
    col4, col5, col6 = st.columns([1, 1, 2])

    # Pace Card
    with col4:
        create_metric_card(
            title="Average Pace",
            value="07:55",
            unit="/km",
            progress={
                "type": "bar",
                "percentage": 75,
                "color": COLORS["primary"],
                "left_label": "Slower",
                "right_label": "Faster"
            }
        )

    # Steps Card
    with col5:
        create_metric_card(
            title="Steps Taken",
            value="10,120",
            icon=create_steps_icon()
        )

    # Workout Frequency Card
    with col6:
        # Create weekly frequency data for chart
        days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        values = [2, 3, 2.5, 4, 3, 5, 6]
        
        create_metric_card(
            title="Workout Frequency",
            value="",  # No value for this card as the chart is the main content
            chart={
                "type": "bar",
                "x": days,
                "y": values,
                "height": 230
            }
        )

    # ===== THIRD ROW - DURATION TREND ===== #
    col7, _ = st.columns([3, 1])

    with col7:
        # Area chart for trend
        dates = pd.date_range(start='2025-03-01', periods=30)
        
        # Create smooth data with some randomness
        x = np.linspace(0, 10, 30)
        smooth_y = 60 + 20 * np.sin(x) + np.random.normal(0, 5, 30)
        
        create_metric_card(
            title="Workout Duration Trend",
            value="1<span class='unit'>h</span> 5<span class='unit'>m</span>",
            chart={
                "type": "line",
                "x": dates,
                "y": smooth_y,
                "height": 180
            }
        )

def render_sidebar():
    """Render the sidebar with additional controls"""
    with st.sidebar:
        st.title("Dashboard Controls")
        st.subheader("Data Source")
        data_source = st.radio("Select Data Source", ["Sample Data", "Database Connection"])
        
        if data_source == "Database Connection":
            st.text_input("Host", "localhost")
            st.text_input("Database", "fitness_tracker")
            st.text_input("Username")
            st.text_input("Password", type="password")
            st.button("Connect")
        
        st.subheader("Export Options")
        export_format = st.selectbox("Export Format", ["CSV", "Excel", "PDF"])
        st.button("Export Dashboard")
        
        # Add a section for theme customization
        st.subheader("Theme Customization")
        st.color_picker("Primary Color", COLORS["primary"])
        st.color_picker("Secondary Color", COLORS["secondary"])

def render_footer():
    """Render the dashboard footer"""
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #888; font-size: 0.8rem;">
        Personal Exercise Dashboard • Powered by Streamlit • Last updated: April 2025
    </div>
    """, unsafe_allow_html=True)

# ===== MAIN APPLICATION ===== #
if __name__ == "__main__":
    # Set dark mode as the base theme for the entire dashboard
    # This better matches the screenshot you shared
    st.markdown("""
    <style>
    /* Dark theme styles */
    .main {
        background-color: #121212;
        color: white;
    }
    .stApp {
        background-color: #121212;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    .stSelectbox > div > div {
        background-color: #333333;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render all dashboard components
    render_dashboard()
    render_sidebar()
    render_footer()
