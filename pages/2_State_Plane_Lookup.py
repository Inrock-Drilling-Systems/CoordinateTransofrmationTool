import streamlit as st
import math
import pandas as pd
import json
import requests
from shapely.geometry import Point, shape
from pyproj import CRS, Transformer
from pyproj.exceptions import ProjError
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

def convert_wgs_to_spcs(lat, lon, spcs_zone_code):
    """
    Converts WGS84 geographic coordinates to SPCS83 projected coordinates.
    Returns a tuple (easting, northing) or (None, None) on error.
    """
    try:
        source_crs = CRS("EPSG:4326")
        target_crs = CRS(f"EPSG:{spcs_zone_code}")
        transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
        easting, northing = transformer.transform(lon, lat)
        return easting, northing
    except ProjError as e:
        st.error(f"Transformation Error: Could not transform coordinates. Please check that the EPSG code '{spcs_zone_code}' is valid and corresponds to the Lat/Lon provided.")
        return None, None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None, None

def convert_spcs_to_wgs(easting, northing, spcs_zone_code):
    """Converts SPCS83 projected coordinates to WGS84 geographic coordinates."""
    try:
        source_crs = CRS(f"EPSG:{spcs_zone_code}")
        target_crs = CRS("EPSG:4326")
        transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
        lon, lat = transformer.transform(easting, northing)
        return lon, lat
    except ProjError:
        st.error(f"Transformation Error: Please check your input values and the selected SPCS Zone.")
        return None, None

def dd_to_dms(dd):
    """Converts a decimal degree value to its positive D, M, S components."""
    if dd is None: return 0, 0, 0
    sign = -1 if dd < 0 else 1
    dd = abs(dd)
    degrees = math.floor(dd)
    minutes_float = (dd - degrees) * 60
    minutes = math.floor(minutes_float)
    seconds = (minutes_float - minutes) * 60
    return degrees, minutes, seconds

def dms_to_dd(degrees, minutes, seconds, hemisphere):
    """Converts D, M, S and a hemisphere to a decimal degree value."""
    degrees = degrees or 0
    minutes = minutes or 0
    seconds = seconds or 0
    dd = degrees + (minutes / 60) + (seconds / 3600)
    if hemisphere in ['S', 'W']:
        return -dd
    return dd

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
st.write("Page Updated: June 11th, 2025")

st.write(
    """
    Use this tool to find State Plane Coordinate System (SPCS) zone information
    by either selecting a U.S. county or providing Latitude/Longitude coordinates.
    """
)

tab_county, tab_lat_lon, tab_point_converter, tab_dms_converter = st.tabs([
    "Lookup by County",
    "Lookup by Lat/Lon",
    "Single Point Conversion by SPCS83 Zone",
    "DD <-> DMS Converter"
])

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

# --- TAB 3: Interactive Point Converter (New Combined Tab) ---
with tab_point_converter:
    st.header("Live Bidirectional Point Converter")

    # --- Create Formatted List for Dropdown ---
    # We iterate through the zones dictionary to create the "FIPS - Name" format.
    # We sort it by the plain text name (the key) to keep the list organized alphabetically.
    formatted_zone_options = [
        f"{fips} - {name}" for name, fips in sorted(spsc83_zones.items())
    ]

    # --- State Management ---
    if 'init_done' not in st.session_state:
        st.session_state.lat = 29.5573  # Pearland, TX
        st.session_state.lon = -95.2835  # Pearland, TX
        st.session_state.easting = 0.0
        st.session_state.northing = 0.0
        # The key must now match the formatted string exactly
        st.session_state.zone_display = "4204 - Texas South Central (USft)"
        st.session_state.last_changed = 'wgs'
        st.session_state.init_done = True


    # --- Callback Functions ---
    def wgs_changed():
        st.session_state.last_changed = 'wgs'


    def spcs_changed():
        st.session_state.last_changed = 'spcs'


    def zone_changed():
        # When zone changes, default to recalculating from WGS coordinates
        st.session_state.last_changed = 'wgs'


    # --- Main Conversion Logic ---

    # 1. Parse the formatted string from the dropdown to get the plain text name
    # The format is "FIPS - Name", so we split it and take the second part.
    plain_text_name = st.session_state.zone_display.split(' - ', 1)[1]

    # 2. Use the plain text name to look up FIPS and then EPSG, as before.
    source_fips = spsc83_zones.get(plain_text_name)
    source_epsg = spcs83_to_epsg.get(source_fips) if source_fips else None

    if source_epsg:
        if st.session_state.last_changed == 'wgs':
            easting, northing = convert_wgs_to_spcs(st.session_state.lat, st.session_state.lon, source_epsg)
            st.session_state.easting = easting
            st.session_state.northing = northing
            st.session_state.last_changed = 'none'

        elif st.session_state.last_changed == 'spcs':
            lon, lat = convert_spcs_to_wgs(st.session_state.easting, st.session_state.northing, source_epsg)
            st.session_state.lon = lon
            st.session_state.lat = lat
            st.session_state.last_changed = 'none'

    # --- UI Layout ---
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        st.subheader("WGS84")
        st.number_input("Latitude", key='lat', format="%.8f", on_change=wgs_changed)
        st.number_input("Longitude", key='lon', format="%.8f", on_change=wgs_changed)

        # The UI for the middle column is now self-contained
        with col2:
            st.subheader("SPCS83 Zone")
            st.selectbox(
                "Select Zone:",
                options=formatted_zone_options,
                key='zone_display',
                on_change=zone_changed,
            )
            # Use st.write with <br> to add vertical space
            st.write("<br><br>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center; font-size: 4em;'>⇌</h1>", unsafe_allow_html=True)

    with col3:
        st.subheader("SPCS83 (USft)")
        st.number_input("Easting", key='easting', format="%.4f", on_change=spcs_changed)
        st.number_input("Northing", key='northing', format="%.4f", on_change=spcs_changed)

with tab_dms_converter:
    st.header("Live Decimal Degree <-> DMS Converter")

    # --- LATITUDE CONVERTER ---
    st.subheader("Latitude Conversion")

    # Initialize session state for this converter
    if 'lat_init' not in st.session_state:
        st.session_state.lat_dd = 29.557300  # Default to your area in Pearland, TX
        st.session_state.lat_hemi = "N"
        st.session_state.lat_d, st.session_state.lat_m, st.session_state.lat_s = dd_to_dms(st.session_state.lat_dd)
        st.session_state.lat_last_changed = 'none'
        st.session_state.lat_init = True


    # Callbacks to track which side was changed
    def lat_dd_changed():
        st.session_state.lat_last_changed = 'dd'


    def lat_dms_changed():
        st.session_state.lat_last_changed = 'dms'


    # Logic to run the appropriate conversion
    if st.session_state.lat_last_changed != 'none':
        if st.session_state.lat_last_changed == 'dd':
            st.session_state.lat_hemi = "N" if st.session_state.lat_dd >= 0 else "S"
            st.session_state.lat_d, st.session_state.lat_m, st.session_state.lat_s = dd_to_dms(st.session_state.lat_dd)
        elif st.session_state.lat_last_changed == 'dms':
            st.session_state.lat_dd = dms_to_dd(st.session_state.lat_d, st.session_state.lat_m, st.session_state.lat_s,
                                                st.session_state.lat_hemi)
        st.session_state.lat_last_changed = 'none'

    # UI Layout for the Latitude Converter
    lat_col1, lat_col2, lat_col3 = st.columns([2.5, 1, 2.5])
    with lat_col1:
        st.number_input("Decimal Latitude", key='lat_dd', format="%.8f", on_change=lat_dd_changed)
    with lat_col2:
        # This container uses Flexbox to perfectly center the arrow.
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; height: 89px;">
                <p style="font-size: 3em; font-weight: bold; margin: 0; padding: 0;">⇌</p>
            </div>
        """, unsafe_allow_html=True)
    with lat_col3:
        hemi_col, d_col, m_col, s_col = st.columns([0.8, 1, 1, 1.2])
        with hemi_col: st.radio(" ", options=["N", "S"], key='lat_hemi', on_change=lat_dms_changed, horizontal=True)
        with d_col: st.number_input("Deg (°)", key='lat_d', min_value=0, step=1, on_change=lat_dms_changed)
        with m_col: st.number_input("Min (')", key='lat_m', min_value=0, step=1, on_change=lat_dms_changed)
        with s_col: st.number_input("Sec (\")", key='lat_s', min_value=0.0, format="%.4f", on_change=lat_dms_changed)

    st.divider()

    # --- LONGITUDE CONVERTER ---
    st.subheader("Longitude Conversion")

    if 'lon_init' not in st.session_state:
        st.session_state.lon_dd = -95.283500  # Default to your area in Pearland, TX
        st.session_state.lon_hemi = "W"
        st.session_state.lon_d, st.session_state.lon_m, st.session_state.lon_s = dd_to_dms(st.session_state.lon_dd)
        st.session_state.lon_last_changed = 'none'
        st.session_state.lon_init = True


    def lon_dd_changed():
        st.session_state.lon_last_changed = 'dd'


    def lon_dms_changed():
        st.session_state.lon_last_changed = 'dms'


    # Logic for Longitude
    if st.session_state.lon_last_changed != 'none':
        if st.session_state.lon_last_changed == 'dd':
            st.session_state.lon_hemi = "E" if st.session_state.lon_dd >= 0 else "W"
            st.session_state.lon_d, st.session_state.lon_m, st.session_state.lon_s = dd_to_dms(st.session_state.lon_dd)
        elif st.session_state.lon_last_changed == 'dms':
            st.session_state.lon_dd = dms_to_dd(st.session_state.lon_d, st.session_state.lon_m, st.session_state.lon_s,
                                                st.session_state.lon_hemi)
        st.session_state.lon_last_changed = 'none'

    # UI for Longitude
    lon_col1, lon_col2, lon_col3 = st.columns([2.5, 1, 2.5])
    with lon_col1:
        st.number_input("Decimal Longitude", key='lon_dd', format="%.8f", on_change=lon_dd_changed)
    with lon_col2:
        # This container uses Flexbox to perfectly center the arrow.
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; height: 89px;">
                <p style="font-size: 3em; font-weight: bold; margin: 0; padding: 0;">⇌</p>
            </div>
        """, unsafe_allow_html=True)
    with lon_col3:
        hemi_col, d_col, m_col, s_col = st.columns([0.8, 1, 1, 1.2])
        with hemi_col: st.radio(" ", options=["E", "W"], key='lon_hemi', on_change=lon_dms_changed, horizontal=True)
        with d_col: st.number_input("Deg (°)", key='lon_d', min_value=0, step=1, on_change=lon_dms_changed)
        with m_col: st.number_input("Min (')", key='lon_m', min_value=0, step=1, on_change=lon_dms_changed)
        with s_col: st.number_input("Sec (\")", key='lon_s', min_value=0.0, format="%.4f", on_change=lon_dms_changed)

st.markdown("---")
st.markdown("Disclaimer: This tool provides general guidance. For precise official coordinates, always consult with a "
            "licensed surveyor or the relevant state agency.")