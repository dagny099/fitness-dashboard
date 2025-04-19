import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.header('Fitness Dashboard Login')
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

def logout():
    st.subheader("👋🏽 You're now logged out")
    if st.button("Reset"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

dashboard = st.Page("dash.py", title="Monthly View", icon=":material/dashboard:", default=True)

calendar = st.Page("calendar_more.py", title="Detailed Stats", icon=":material/calendar_month:")

bugs = st.Page("tools/bugs.py", title="Bug reports", icon=":material/bug_report:")
alerts = st.Page("tools/alerts.py", title="System alerts", icon=":material/notification_important:")
test = st.Page("tools/testcard.py", title="Test", icon=":material/search:")
history = st.Page("tools/history.py", title="History", icon=":material/history:")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Reports": [dashboard],
            "Calendar": [calendar],
            "Tools": [bugs, alerts, test, history],
            "Account": [logout_page],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()

#Add a thank you for streamlit-calendar
