import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
from datetime import datetime

df = pd.read_csv('src/user2632022_workout_history.csv')

# Custom date parsing function
def parse_date(date_string):
    """Function to parse date strings in various formats"""
    date_formats = [
        '%b. %d, %Y',  # Aug. 1, 2024
        '%d-%b-%y',    # 31-Jul-24
        '%d-%b-%Y',    # 31-Jul-2024
        '%B %d, %Y',   # July 31, 2024
        '%d-%m-%y',    # 20-06-23
        '%Y-%m-%d'     # 2024-08-01 (in case you have any in this format)
    ]   
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass    
    return None


def assign_color(criteria):
    if criteria > 5:
        return "#1f77b4"  # Blue
    elif (criteria >= 2) & (criteria < 5):
        return "#ff7f0e"  # Orange
    else:
        return "#888888"  # Default gray

# CATEGORIZE BY COLOR
df["color"] = df["Distance (mi)"].apply(assign_color)

df['Workout Date'] = df['Workout Date'].apply(lambda x: parse_date(str(x)))
df["start"] = df["Workout Date"]
df["end"] = df["start"]
df["title"] = df["Link"]
df["start"] = pd.to_datetime(df["start"]).dt.date.astype(str)
df["end"] = pd.to_datetime(df["end"]).dt.date.astype(str)

events = df[["title","start","end","color"]].to_dict(orient="records")


# Configure calendar options
calendar_options = {
    "initialView": "dayGridMonth",  # Sets the view to month
    "editable": False,              # Disables editing events
    "selectable": False             # Disables date selection
}
custom_css = """
.fc .fc-daygrid-event {
    background-color: #1f77b4;
    color: white;
    border: none;
}
"""

response = calendar(
    events=events,
    options=calendar_options,
    custom_css=custom_css,
    key='calendar', # Assign a widget key to prevent state loss
    )

# st.write(response)
# 📆 Display events below the calendar
st.markdown("### 📋 Events in View")
if response and "eventsSet" in response and "events" in response["eventsSet"]:
    for event in response["eventsSet"]["events"]:
        title = event.get("title", "Untitled")
        start = event.get("start", "No date")
        st.write(f"📅 **{start}** — [{title}]({title})")
else:
    st.info("No events to display.")

