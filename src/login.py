# --------------------------------------------------------------------------
# login.py
# This file is part of the Streamlit app for the Fitness Dashboard.
# --------------------------------------------------------------------------

import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

backimage = 'https://raw.githubusercontent.com/dagny099/dagny099.github.io/ff96cc0d1cbc65fbe5a0789eb00d73aff65c4059/assets/images/midjourney/the-mycelium-web/hr-beautiful-forrest-electric-blue-mycelium-yellow-dots-03.png'

st.markdown(f"""
<style>
.stApp {{
    background-image: linear-gradient(90deg, rgb(0, 102, 204), rgb(102, 255, 255));
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Helvetica Neue', sans-serif;
}}

.welcome-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: white;
    background: rgba(0, 0, 0, 0.5);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    max-width: 800px;
    margin: 0 auto;
    font-family: 'Helvetica Neue', sans-serif;
}}
.header {{
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 5px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}}
.subheader {{
    font-size: 2rem;
    font-weight: 500;
    text-align: center;
    margin-bottom: 20px;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
}}
.description {{
    font-size: 1.2rem;
    font-weight: 300;
    margin-bottom: 30px;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}}
.branding-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
    padding: 20px;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
}}
.branding-image {{
    width: 100%;
    height: auto;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    transition: transform 0.3s;
}}
.branding-image:hover {{
    transform: scale(1.05);
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.7);
}}
.branding-image:active {{
    transform: scale(0.95);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}}
.branding-image:focus {{
    outline: none;
    box-shadow: 0 0 0 4px rgba(0, 102, 204, 0.5);
    border-radius: 10px;
}}

div.stButton > button {{
    background-color: rgba(0, 0, 0, 0.5);
    align-items: center;
    text-align: center;
    color: white;
    font-weight: bold;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    cursor: pointer;
    transition: 0.3s;
}}

div.stButton > button:hover {{
    background-color: #146d8d;
    transform: scale(1.02);
}}
</style>
""", unsafe_allow_html=True)

# Render login card container
with st.container():
    st.markdown("""
        <div class="welcome-container">
            <h1 class="header">Fitness Dashboard</h1>
            <h2 class="subheader">Track your progress, pace, and power</h2>
            <p class="description">Log in to access your personalized dashboard 🏃‍♀️</p>
                <img class="branding-image" src="https://raw.githubusercontent.com/dagny099/dagny099.github.io/master/assets/images/portfolio/login_page_image_v1.png" alt="branding logo">
        </div>
        """, unsafe_allow_html=True)
        
left_col, center_col, right_col = st.columns([1, 2, 1])

with center_col:
    login = st.button("Log In")

# Add logic
if login:
    st.session_state.logged_in = True
    st.rerun()
