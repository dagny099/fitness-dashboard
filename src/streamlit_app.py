import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Development mode bypass for testing
def check_dev_mode():
    """Check if development mode is enabled via environment variable or URL parameter"""
    # Check environment variable
    if os.getenv('STREAMLIT_DEV_MODE', '').lower() == 'true':
        return True
    
    # Check URL parameter (if available)
    try:
        query_params = st.query_params
        if query_params.get('dev_mode', '').lower() == 'true':
            return True
    except:
        pass
    
    return False

# Auto-login in development mode
if check_dev_mode() and not st.session_state.logged_in:
    st.session_state.logged_in = True

def logout():
    st.subheader("👋🏽 You're now logged out")
    if st.button("Reset"):
        st.session_state.logged_in = False
        st.rerun()

# Set up the page with MULTIPAGE NAVIGATION
login_page = st.Page("views/login.py", title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

intelligence = st.Page("views/intelligence.py", title="AI Intelligence", icon="🧠", default=True)
model_management = st.Page("views/model_management.py", title="Model Management", icon="🤖")

calendar = st.Page("views/calendar_more.py", title="Detailed Stats", icon=":material/calendar_month:")
dashboard_monthly = st.Page("views/dash.py", title="Monthly View", icon=":material/dashboard:")

# bugs = st.Page("tools/bugs.py", title="Trends", icon=":material/data_exploration:")
trends = st.Page("views/tools/trends.py", title="Trends", icon=":material/data_exploration:")
query_db = st.Page("views/fitness-overview.py", title="SQL Query", icon=":material/database_search:")
mapping = st.Page("views/tools/mapping.py", title="Mapping", icon=":material/add_location:")
history = st.Page("views/tools/history.py", title="Workout History", icon=":material/table_chart:")
choco_effect = st.Page("views/choco_effect.py", title="The Choco Effect", icon="🐕")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Intelligence": [intelligence, model_management],
            "Calendar": [dashboard_monthly, calendar],
            "Reports": [choco_effect],
            "Tools": [trends, mapping, query_db, history],
            "Account": [logout_page],
        }
    )
else:
    pg = st.navigation([login_page])

st.set_page_config(
    page_title="Fitness Dashboard",
    page_icon="📊",
    layout="wide",
    # initial_sidebar_state="collapsed",
    menu_items={
        "Get help": "https://www.streamlit.io/",
        "Report a bug": "mailto:dagny099@gmail.com",
    }
)

pg.run()

#Add a thank you for streamlit-calendar
