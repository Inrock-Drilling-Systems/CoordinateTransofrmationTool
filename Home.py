import streamlit as st

st.set_page_config(
    page_title="Inrock Guidance",
    page_icon="🌍",
    layout="wide" # or "wide" if you prefer
)

st.title("Welcome to the Inrock Transformation Tool")
st.write("Version 0.4 - Feature Expansion")
st.write("Page Updated: June 1st, 2025")

st.write(
    """
    This application allows you to perform 3D coordinate transformations
    and visualize survey data.

    **To get started, please select 'Survey Export Transformations' from the sidebar on the left.**
    """
)

st.info("Need to transform coordinates? Navigate to the 'Survey Export Transformations' page.")

st.info("Need to find what zone to use? Navigate to the 'State Plane Lookup' page.")

# You can add more content here, like an 'About' section, instructions, or a project overview.