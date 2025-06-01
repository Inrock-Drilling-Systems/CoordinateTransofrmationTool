import streamlit as st
import pandas as pd
import json
import requests
from shapely.geometry import Point, shape
import pyproj
from src.constants import spcs83_to_epsg, county_spcs_mapping, spsc83_zones

# --- Function to lookup SPCS by Lat/Lon (Requires actual spatial data) ---
# This function is conceptual and would require a GeoDataFrame
# with county polygons and their associated SPCS info.
# For demo, it will return placeholder.
def lookup_spcs_by_lat_lon(latitude, longitude, geo_data):
    """
    Looks up the State Plane Zone given latitude and longitude.
    This is a placeholder and requires a GeoDataFrame for actual implementation.
    `geo_data` would typically be a geopandas GeoDataFrame with 'geometry' (polygon)
    and 'SPCS_FIPS' / 'SPCS_Name' columns.
    """
    point = Point(longitude, latitude) # shapely Point (lon, lat)

    # In a real scenario, you would iterate through geo_data features
    # and check if point.within(feature.geometry)
    # For now, return a fixed example:
    if 29 <= latitude <= 36 and -106 <= longitude <= -93: # Rough bbox for Texas
        return "Texas South Central", "4204" # Placeholder for Texas
    else:
        return "Not Found (Placeholder)", "N/A"

# --- Streamlit App Layout ---
# st.set_page_config(layout="wide")
# st.title("State Plane Coordinate System Lookup")

st.set_page_config(
    page_title="Inrock Guidance - SPCS83 Lookup",
    page_icon="🌍",
    layout="centered" # or "wide" if you prefer
)

st.title("SPCS83 Lookup")
st.write("Version 0.4 - Feature Expansion")
st.write("Page Updated: June 1st, 2025")


st.write(
    """
    Use this tool to find State Plane Coordinate System (SPCS) zone information
    by either selecting a U.S. county or providing Latitude/Longitude coordinates.
    """
)

# Create tabs for different lookup methods
tab_county, tab_lat_lon = st.tabs(["Lookup by County", "Lookup by Lat/Lon"])

with tab_county:
    st.header("Lookup by County")
    st.title("**Phase: Beta :: Report Bugs on Discovery**")
    selected_state = st.selectbox(
        "Select State:",
        options=list(county_spcs_mapping.keys()),
        key="state_select"
    )

    if selected_state:
        counties_in_state = list(county_spcs_mapping[selected_state].keys())
        selected_county = st.selectbox(
            f"Select County in {selected_state}:",
            options=counties_in_state,
            key="county_select"
        )

        if selected_county:
            st.subheader("Result:")
            zone_info = county_spcs_mapping[selected_state][selected_county]
            st.success(f"**Zone Name:** {zone_info['zone_name']}")
            st.success(f"**Zone FIPS:** {zone_info['fips']}")
            if zone_info['fips'] in spcs83_to_epsg:
                st.info(f"**Corresponding EPSG (USft):** EPSG:{spcs83_to_epsg[zone_info['fips']]}")
            else:
                st.warning("EPSG code not found in constants for this FIPS.")
        else:
            st.info("Please select a county.")
    else:
        st.info("Please select a state.")


with tab_lat_lon:
    st.header("Lookup by Latitude/Longitude")
    st.title("**Phase: Alpha :: Do not trust output**")
    lat_input = st.number_input("Enter Latitude:", min_value=-90.0, max_value=90.0, value=30.0, format="%.6f", key="lat_input")
    lon_input = st.number_input("Enter Longitude:", min_value=-180.0, max_value=180.0, value=-95.0, format="%.6f", key="lon_input")

    if st.button("Lookup SPCS Zone", key="lat_lon_lookup_button"):
        if lat_input is not None and lon_input is not None:
            st.subheader("Result:")
            # Call the lookup function (currently a placeholder)
            # In a real app, 'geo_data' would be your loaded GeoDataFrame
            zone_name, zone_fips = lookup_spcs_by_lat_lon(lat_input, lon_input, geo_data=None)

            if zone_name != "Not Found (Placeholder)":
                st.success(f"**Zone Name:** {zone_name}")
                st.success(f"**Zone FIPS:** {zone_fips}")
                if zone_fips in spcs83_to_epsg:
                    st.info(f"**Corresponding EPSG (USft):** EPSG:{spcs83_to_epsg[zone_fips]}")
                else:
                    st.warning("EPSG code not found in constants for this FIPS.")
            else:
                st.warning("Could not determine SPCS Zone for the given coordinates (placeholder data used).")
        else:
            st.warning("Please enter valid Latitude and Longitude.")

st.markdown("---")
st.markdown("Disclaimer: This tool provides general guidance. For precise official coordinates, always consult with a licensed surveyor or the relevant state agency.")