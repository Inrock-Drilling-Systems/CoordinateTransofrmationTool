import streamlit as st
import pandas as pd
from src.transformations import transform_coordinates
from src.remove_and_reformat import process_survey_csv
from src.create_map import create_map
from src.constants import STATE_PLANE_ZONES
from streamlit.components.v1 import html
from src.generate_kmz import generate_kmz
from src.pretty_dataframe import correct_output

# Open Streamlit in Wide Mode
st.set_page_config(layout="wide")

# Title
st.title("3D Coordinate Transformation Tool v0.2")

# Layout: Divide the page into three columns
left_column, middle_column, right_column = st.columns([1, 1, 1])  # Equal thirds

# Dropdown menu in the top middle column
with middle_column:
    st.header("Select Region for State Plane CRS")
    region = st.selectbox(
        "Select your region:",
        list(STATE_PLANE_ZONES.keys()),
        key="region_selectbox"  # Add a unique key
    )
    state_plane_fips = STATE_PLANE_ZONES[region]
    st.write(f"Selected State Plane FIPS: {state_plane_fips}")

# Left column: Tie-in points
with left_column:
    st.header("Tie-in Points")

    # Add single checkbox for elevation linking at the top
    link_elevations = st.checkbox("Link All Elevations", value=True,
                                  help="When checked, State Plane elevations will match Local elevations")

    # Local Entry
    st.subheader("Local Entry (Local Coordinates)")
    col1, col2, col3 = st.columns(3)
    with col1:
        local_entry_away = st.text_input("Away", "0.00", key="local_entry_away")
    with col2:
        local_entry_right = st.text_input("Right", "0.00", key="local_entry_right")
    with col3:
        if 'local_entry_elevation' not in st.session_state:
            st.session_state.local_entry_elevation = "0.00"
        local_entry_elevation = st.text_input("Elevation", st.session_state.local_entry_elevation, key="local_entry_elevation")
        if local_entry_elevation != st.session_state.local_entry_elevation and link_elevations:
            st.session_state.tie_in_entry_elevation = local_entry_elevation
            st.session_state.local_entry_elevation = local_entry_elevation

    # Tie-In Entry
    st.subheader("Tie-In Entry (State Plane Coordinates)")
    col1, col2, col3 = st.columns(3)
    with col1:
        tie_in_entry_easting = st.text_input("Easting", "3055956.05", key="tie_in_entry_away")
    with col2:
        tie_in_entry_northing = st.text_input("Northing", "13874745.74", key="tie_in_entry_right")
    with col3:
        if 'tie_in_entry_elevation' not in st.session_state:
            st.session_state.tie_in_entry_elevation = local_entry_elevation if link_elevations else "0.00"
        tie_in_entry_elevation = st.text_input("Elevation",
                                             value=st.session_state.tie_in_entry_elevation,
                                             key="tie_in_entry_elevation",
                                             disabled=link_elevations)

    # Local Exit
    st.subheader("Local Exit (Local Coordinates)")
    col1, col2, col3 = st.columns(3)
    with col1:
        local_exit_away = st.text_input("Away", "2000.00", key="local_exit_away")
    with col2:
        local_exit_right = st.text_input("Right", "0.00", key="local_exit_right")
    with col3:
        if 'local_exit_elevation' not in st.session_state:
            st.session_state.local_exit_elevation = "0.00"
        local_exit_elevation = st.text_input("Elevation", st.session_state.local_exit_elevation, key="local_exit_elevation")
        if local_exit_elevation != st.session_state.local_exit_elevation and link_elevations:
            st.session_state.tie_in_exit_elevation = local_exit_elevation
            st.session_state.local_exit_elevation = local_exit_elevation

    # Tie-In Exit
    st.subheader("Tie-In Exit (State Plane Coordinates)")
    col1, col2, col3 = st.columns(3)
    with col1:
        tie_in_exit_easting = st.text_input("Easting", "3102522.92", key="tie_in_exit_away")
    with col2:
        tie_in_exit_northing = st.text_input("Northing", "13761445.36", key="tie_in_exit_right")
    with col3:
        if 'tie_in_exit_elevation' not in st.session_state:
            st.session_state.tie_in_exit_elevation = local_exit_elevation if link_elevations else "0.00"
        tie_in_exit_elevation = st.text_input("Elevation",
                                            value=st.session_state.tie_in_exit_elevation,
                                            key="tie_in_exit_elevation",
                                            disabled=link_elevations)

# Middle column: File upload and output
with middle_column:
    # File upload
    st.header("Upload CSV of Local Coordinates")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Read CSV into a DataFrame & Extract required information
        data = process_survey_csv(uploaded_file)

        # Ensure required columns exist
        required_columns = ["Point", "Away", "Right", "Elevation", "Description"]
        columns_present = all(col in data.columns for col in required_columns)

        if not columns_present:
            st.error(f"Uploaded file must include the following columns: {required_columns}")
        else:
            # Refactor data: Add Local Entry and Local Exit at the top
            local_entry_row = {
                "Point": 1,
                "Away": float(local_entry_away),
                "Right": float(local_entry_right),
                "Elevation": float(local_entry_elevation),
                "Description": "Local Entry Verify"
            }
            local_exit_row = {
                "Point": 2,
                "Away": float(local_exit_away),
                "Right": float(local_exit_right),
                "Elevation": float(local_exit_elevation),
                "Description": "Local Exit Verify"
            }

            # Increment Point column in the uploaded data
            data["Point"] = range(3, 3 + len(data))

            # Add Local Entry and Local Exit to the top
            refactored_data = pd.concat(
                [pd.DataFrame([local_entry_row, local_exit_row]), data],
                ignore_index=True
            )

            # st.write("Refactored Data:")
            # st.write(refactored_data)

            # Transform coordinates
            tie1_local = [float(local_entry_away), float(local_entry_right), float(local_entry_elevation)]
            tie2_local = [float(local_exit_away), float(local_exit_right), float(local_exit_elevation)]
            tie1_state = [float(tie_in_entry_easting), float(tie_in_entry_northing), float(tie_in_entry_elevation)]
            tie2_state = [float(tie_in_exit_easting), float(tie_in_exit_northing), float(tie_in_exit_elevation)]

            try:
                refactored_data = transform_coordinates(refactored_data, tie1_local, tie1_state, tie2_local, tie2_state, state_plane_fips)
                refactored_data = correct_output(refactored_data)
                st.write("Transformed Coordinates:")
                st.write(refactored_data)

                # Save transformed coordinates to a CSV
                csv = refactored_data.to_csv(index=False)
                st.download_button("Download Transformed Data", csv, "transformed_data.csv", "text/csv")
            except ValueError as ve:
                st.error(f"Error in transformation: {ve}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")



# Right column: Map visualization
with right_column:
    st.header("Map Overlay")

    if uploaded_file is not None:
        try:
            # Generate the map using the create_map function
            folium_map = create_map(
                refactored_data['Latitude'][2:],
                refactored_data['Longitude'][2:],
                refactored_data['Altitude'][2:]
            )

            # Render the map as HTML
            map_html = folium_map._repr_html_()
            html(map_html, height=500)  # Embed the HTML map in Streamlit
        except KeyError:
            st.error("Map cannot be generated. Ensure transformed data includes latitude and longitude.")

    st.header("KMZ Output")

    # Generate the KMZ file
    if st.button("Generate KMZ File"):
        kmz_path = generate_kmz(refactored_data['Longitude'][2:], refactored_data['Latitude'][2:], refactored_data['Elevation'][2:], refactored_data['Description'][2:])
        with open(kmz_path, "rb") as file:
            st.download_button(
                label="Download KMZ",
                data=file,
                file_name="transformed_data.kmz",
                mime="application/vnd.google-earth.kmz",
            )
