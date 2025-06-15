import streamlit as st

def display_header():
    """Displays a centered logo header on the page."""
    # UPDATED: Changed column ratios to make the center column narrower
    col1, col2, col3 = st.columns([2.5, 1, 2.5])

    with col1:
        st.write("") # Empty space

    with col2:
        # UPDATED: Changed 'use_column_width' to 'use_container_width'
        st.image("rss/inrock_logo.png", use_container_width=True)

    with col3:
        st.write("") # Empty space