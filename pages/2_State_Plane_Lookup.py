import streamlit as st
import math
import re
from datetime import date
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point, shape
from pyproj import CRS, Transformer
from pyproj.exceptions import ProjError
from src.constants import spcs83_to_epsg, county_spcs_mapping, spsc83_zones
from src.shared_ui import display_header

# --- Streamlit App Layout ---
st.set_page_config(
    page_title="Inrock Guidance - SPCS83 Lookup",
    page_icon="../rss/inrock_icon.png",
    layout="wide"
)

display_header()

# --- Data Loading Function with Caching ---
@st.cache_data
def load_data(shapefile_path):
    """
    Loads the shapefile into a GeoDataFrame, caches it, and re-projects to WGS84.
    """
    try:
        gdf = gpd.read_file(shapefile_path)
        # Convert the GeoDataFrame's CRS to WGS84 (EPSG:4326) to match lat/lon input
        gdf = gdf.to_crs("EPSG:4326")
        return gdf
    except Exception as e:
        st.error(f"Error loading shapefile: {e}")
        return None

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

def parse_dms_string(dms_str):
    """
    Parses a DMS string into components using regular expressions.
    Handles formats like: 40°44'52.2"N, 40 44 52.2 N, -98 11 22.5
    Returns (degrees, minutes, seconds, hemisphere) or None if parsing fails.
    """
    dms_str = dms_str.strip()
    # This regex captures numbers separated by common delimiters, and an optional hemisphere letter.
    match = re.match(r'(-?[\d\.]+)[°\s\-:]+([\d\.]+)[`\'\s\-:]+([\d\.]+)"?[\s]*([NSEW]?)', dms_str, re.IGNORECASE)
    if not match:
        return None  # Return None if the format is not recognized

    groups = match.groups()
    degrees = float(groups[0])
    minutes = float(groups[1])
    seconds = float(groups[2])
    hemisphere = groups[3].upper()

    # If a hemisphere is specified, ensure degrees is positive
    if hemisphere and degrees < 0:
        degrees = abs(degrees)

    return degrees, minutes, seconds, hemisphere

def dd_to_dms(dd):
    """Converts a decimal degree value to its positive D, M, S components."""
    if dd is None: return 0, 0, 0
    dd = abs(dd)
    degrees = math.floor(dd)
    minutes_float = (dd - degrees) * 60
    minutes = math.floor(minutes_float)
    seconds = (minutes_float - minutes) * 60
    return degrees, minutes, seconds

def dms_to_dd(degrees, minutes, seconds, hemisphere=''):
    """Converts D, M, S and an optional hemisphere to a decimal degree value."""
    degrees = degrees or 0
    minutes = minutes or 0
    seconds = seconds or 0
    dd = abs(degrees) + (minutes / 60) + (seconds / 3600)
    if hemisphere in ['S', 'W'] or degrees < 0:
        return -dd
    return dd

# Add this code to define the path and load the data
# Construct the full path to the shapefile
SHAPEFILE = Path(__file__).parent.parent / "shapefiles" / "spcs" / "spcs83_zones.shp"

# Load the shapefile data using the cached function
stateplane_gdf = load_data(SHAPEFILE)

st.title("SPCS83 Lookup")
st.write("Version 0.4 - Feature Expansion")
st.write(f"Page Updated: {date.today().strftime('%B %d, %Y')}")

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

st.title("**Phase: Beta :: Report Bugs on Discovery**")

with tab_county:
    st.header("Lookup by County")
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

    # Check if the shapefile was loaded successfully
    if stateplane_gdf is None:
        st.error(
            "State Plane zones shapefile could not be loaded. Please check the file path: 'shapefiles/spcs/spcs83_zones.shp'")
    else:
        lat_input = st.number_input("Enter Latitude:", min_value=-90.0, max_value=90.0, value=29.7604, format="%.6f",
                                    key="lat_input")
        lon_input = st.number_input("Enter Longitude:", min_value=-180.0, max_value=180.0, value=-95.3698,
                                    format="%.6f", key="lon_input")

        if st.button("Lookup SPCS Zone", key="lat_lon_lookup_button"):
            if lat_input is not None and lon_input is not None:
                # Create a Shapely Point from user input
                user_point = Point(lon_input, lat_input)

                # Find the polygon that contains the user's point
                containing_zone = stateplane_gdf[stateplane_gdf.contains(user_point)]

                st.subheader("Result:")

                if not containing_zone.empty:
                    # Extract the first (and should be only) result
                    zone_data = containing_zone.iloc[0]

                    # !!! IMPORTANT: Replace 'NAME' and 'FIPS' with your actual column names !!!
                    zone_name = zone_data['ZONENAME']
                    zone_fips = zone_data['FIPSZONE']

                    st.success(f"**Zone Name:** {zone_name}")
                    st.success(f"**Zone FIPS:** {zone_fips}")

                    # Convert fips to string for dictionary lookup to be safe
                    if str(zone_fips) in spcs83_to_epsg:
                        st.info(f"**Corresponding EPSG (USft):** EPSG:{spcs83_to_epsg[str(zone_fips)]}")
                    else:
                        st.warning("EPSG code not found in constants for this FIPS.")
                else:
                    st.warning(
                        "Could not determine SPCS Zone. The provided coordinates may be outside the covered area.")
            else:
                st.warning("Please enter valid Latitude and Longitude.")

with tab_point_converter:
    st.header("Live Bidirectional Point Converter")

    # --- Create Formatted List for Dropdown ---
    formatted_zone_options = [
        f"{fips} - {name}" for name, fips in sorted(spsc83_zones.items())
    ]

    # --- State Management ---
    if 'init_done' not in st.session_state:
        st.session_state.lat = 29.540680396105017  # Pearland, TX
        st.session_state.lon = -95.43294457550921  # Pearland, TX
        st.session_state.easting = 0.0
        st.session_state.northing = 0.0
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
    if 'zone_display' in st.session_state and st.session_state.zone_display:
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

        st.markdown(
            """
            <div style="padding-top: 0.5rem; text-align: center;">
                <p style="font-size: 3em; font-weight: bold; margin: 0;">⇌</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.subheader("SPCS83 (USft)")
        st.number_input("Easting", key='easting', format="%.4f", on_change=spcs_changed)
        st.number_input("Northing", key='northing', format="%.4f", on_change=spcs_changed)


with tab_dms_converter:
    st.header("Live Decimal Degree <-> DMS Converter")

    st.subheader("Latitude Conversion")

    if 'lat_dms_init' not in st.session_state:
        st.session_state.lat_dd_val = 29.557300
        st.session_state.lat_dms_str = "29°33'26.2800\"N"
        st.session_state.lat_last_changed = 'none'
        st.session_state.lat_dms_init = True


    def lat_dd_val_changed():
        st.session_state.lat_last_changed = 'dd'


    def lat_dms_str_changed():
        st.session_state.lat_last_changed = 'dms'


    if st.session_state.lat_last_changed != 'none':
        if st.session_state.lat_last_changed == 'dd':
            dd = st.session_state.lat_dd_val
            hemi = "N" if dd >= 0 else "S"
            d, m, s = dd_to_dms(dd)
            st.session_state.lat_dms_str = f'{d}°{m}\'{s:.4f}"{hemi}'
        elif st.session_state.lat_last_changed == 'dms':
            parsed = parse_dms_string(st.session_state.lat_dms_str)
            if parsed:
                d, m, s, hemi = parsed
                if hemi not in ['N', 'S'] and d >= 0:
                    hemi = 'N'
                elif hemi not in ['N', 'S'] and d < 0:
                    hemi = 'S'
                st.session_state.lat_dd_val = dms_to_dd(d, m, s, hemi)
        st.session_state.lat_last_changed = 'none'

    lat_col1, lat_col2, lat_col3 = st.columns([2, 1, 2])
    with lat_col1:
        st.number_input("Decimal Latitude", key='lat_dd_val', format="%.8f", on_change=lat_dd_val_changed)
    with lat_col2:
        # This container uses Flexbox for precise vertical alignment.
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; height: 74px;">
                <p style="font-size: 3em; font-weight: bold; margin: 0; padding: 0;">⇌</p>
            </div>
        """, unsafe_allow_html=True)
    with lat_col3:
        st.text_input("DMS Latitude", key='lat_dms_str', on_change=lat_dms_str_changed,
                      placeholder="e.g., 40 44 52.2 N")

    st.divider()

    st.subheader("Longitude Conversion")

    if 'lon_dms_init' not in st.session_state:
        st.session_state.lon_dd_val = -95.283500
        st.session_state.lon_dms_str = "95°17'0.6000\"W"
        st.session_state.lon_last_changed = 'none'
        st.session_state.lon_dms_init = True


    def lon_dd_val_changed():
        st.session_state.lon_last_changed = 'dd'


    def lon_dms_str_changed():
        st.session_state.lon_last_changed = 'dms'


    if st.session_state.lon_last_changed != 'none':
        if st.session_state.lon_last_changed == 'dd':
            dd = st.session_state.lon_dd_val
            hemi = "E" if dd >= 0 else "W"
            d, m, s = dd_to_dms(dd)
            st.session_state.lon_dms_str = f'{d}°{m}\'{s:.4f}"{hemi}'
        elif st.session_state.lon_last_changed == 'dms':
            parsed = parse_dms_string(st.session_state.lon_dms_str)
            if parsed:
                d, m, s, hemi = parsed
                if hemi not in ['E', 'W'] and d >= 0:
                    hemi = 'E'
                elif hemi not in ['E', 'W'] and d < 0:
                    hemi = 'W'
                st.session_state.lon_dd_val = dms_to_dd(d, m, s, hemi)
        st.session_state.lon_last_changed = 'none'

    lon_col1, lon_col2, lon_col3 = st.columns([2, 1, 2])
    with lon_col1:
        st.number_input("Decimal Longitude", key='lon_dd_val', format="%.8f", on_change=lon_dd_val_changed)
    with lon_col2:
        # This container uses Flexbox for precise vertical alignment.
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: center; height: 74px;">
                <p style="font-size: 3em; font-weight: bold; margin: 0; padding: 0;">⇌</p>
            </div>
        """, unsafe_allow_html=True)
    with lon_col3:
        st.text_input("DMS Longitude", key='lon_dms_str', on_change=lon_dms_str_changed,
                      placeholder="e.g., -98 11 22.5 or 98 11 22.5 W")

st.markdown("---")
st.markdown("Disclaimer: This tool provides general guidance. For precise official coordinates, always consult with a "
            "licensed surveyor or the relevant state agency.")