import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def logout():
    st.subheader("👋🏽 You're now logged out")
    if st.button("Reset"):
        st.session_state.logged_in = False
        st.rerun()

# Set up the page with MULTIPAGE NAVIGATION
login_page = st.Page("login.py", title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

dashboard = st.Page("dash.py", title="Monthly View", icon=":material/dashboard:", default=True)

calendar = st.Page("calendar_more.py", title="Detailed Stats", icon=":material/calendar_month:")

# bugs = st.Page("tools/bugs.py", title="Trends", icon=":material/data_exploration:")
trends = st.Page("tools/trends.py", title="Trends", icon=":material/data_exploration:")
query_db = st.Page("fitness-overview.py", title="SQL Query", icon=":material/database_search:")
mapping = st.Page("tools/mapping.py", title="Mapping", icon=":material/add_location:")
history = st.Page("tools/history.py", title="DataFrame Demo", icon=":material/table_chart:")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Reports": [dashboard],
            "Calendar": [calendar],
            "Tools": [trends, mapping, query_db, history],
            "Account": [logout_page],
        }
    )
else:
    pg = st.navigation([login_page])

st.set_page_config(
    page_title="Fitness Dashboard",
    page_icon=":material/dashboard:",
    layout="wide",
    # initial_sidebar_state="collapsed",
    menu_items={
        "Get help": "https://www.streamlit.io/", 
        "Report a bug": "mailto:dagny099@gmail.com", 
    }
)

pg.run()

#Add a thank you for streamlit-calendar
