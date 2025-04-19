import streamlit as st

# This hides both the sidebar itself and the "≡" hamburger button that would otherwise allow reopening it.
# If you leave off the collapsedControl rule, users will still be able to open the sidebar manually.
hide_sidebar_style = """
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="collapsedControl"] {
        display: none;
    }
</style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# Display Bacgkround:
backimage = 'https://raw.githubusercontent.com/dagny099/dagny099.github.io/ff96cc0d1cbc65fbe5a0789eb00d73aff65c4059/assets/images/midjourney/the-mycelium-web/hr-beautiful-forrest-electric-blue-mycelium-yellow-dots-03.png'
css = f"""
<style>
    .stApp {{
        background-image: url({backimage});
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .branding-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 50vh;
    }}

    .branding-image {{
        max-width: 300px;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0,0,0,0.4);
    }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Create centered image div
image_url = "https://raw.githubusercontent.com/dagny099/dagny099.github.io/ff96cc0d1cbc65fbe5a0789eb00d73aff65c4059/assets/images/favicon/android-chrome-256x256.png"
branding_html = f"""
<div class="branding-container">
    <img class="branding-image" src="{image_url}" alt="branding logo">
</div>
"""
st.markdown(branding_html, unsafe_allow_html=True)
