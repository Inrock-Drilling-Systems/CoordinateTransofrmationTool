import streamlit as st
from datetime import date
from src.shared_ui import display_header

# --- Page Configuration ---
st.set_page_config(
    page_title="Inrock Navigator",
    page_icon="rss/inrock_icon.png",
    layout="wide"
)

display_header()

# --- Main Page Content ---
st.title("Welcome to the Inrock Navigator")
st.write(f"*Last Updated: {date.today().strftime('%B %d, %Y')}*")

st.divider()

# --- Page Layout with Columns ---
col1, col2 = st.columns((2, 1))

with col1:
    st.header("About This Application")
    st.markdown(
        """
        This Inrock Navigator is a comprehensive application for handling spatial data and survey-related tasks. It 
        serves as a one-stop shop for discovering coordinate systems, performing live transformations, and processing 
        raw survey files into actionable data and visual formats. From initial zone lookup to final KML export, this 
        tool provides a complete workflow for Inrock's guidance needs.
        """
    )

    # --- Expander for Detailed Instructions (now expanded by default) ---
    with st.expander("How to Use This Tool", expanded=True):
        st.markdown(
            """
            - **Survey Export Transformation**: Takes As-Drill/Proposed Bore wire files and converts them to the desired SPCS83 and WGS84 coordinates. This is based on provided "tie-in" points obtained externally and allows the user to either download the data directly and/or download a KML file for visual representation.

            - **State Plane Lookup**: Navigate to this page to determine the correct SPCS zone for a given location.
                - *Lookup by County*: Select a state and county to find its FIPS zone code and name.
                - *Lookup by Lat/Lon*: Input a specific Latitude and Longitude to find the corresponding zone using spatial data.

            - **Point & DMS Converters**: Within the 'State Plane Lookup' page, you will find additional tabs for live conversion between WGS84 (Lat/Lon) and SPCS83 coordinates, as well as a utility for converting between Decimal Degrees and Degrees-Minutes-Seconds.
            """
        )

with col2:
    st.subheader("Quick Links")

    st.page_link(
        "pages/1_Survey_Export_Transformation.py",
        label="Survey Export Transformations",
        icon="📄"
    )
    st.page_link(
        "pages/2_State_Plane_Lookup.py",
        label="SPCS Zone & Point Converters",
        icon="🌐"
    )

    st.divider()

    st.link_button(
        "Visit Inrock's Website",
        "https://www.inrock.com/",
        use_container_width=True
    )

st.divider()

st.info(
    "Disclaimer: This tool provides general guidance. For precise official coordinates, always consult with a licensed surveyor or the relevant state agency.")