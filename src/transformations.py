import numpy as np
from pyproj import Transformer
from src.constants import spcs83_to_epsg

def transform_coordinates(data, tie1_local, tie1_state, tie2_local, tie2_state, state_plane_zone):
    """
    Transforms local coordinates to State Plane coordinates (translation + rotation about Tie-In Entry),
    then converts them to Latitude/Longitude.

    Args:
        data: DataFrame containing local coordinates.
        tie1_local: List [Away, Right, Elevation] of tie-in entry (local coordinates).
        tie1_state: List [Easting, Northing, Elevation] of tie-in entry (State Plane coordinates).
        tie2_local: List [Away, Right, Elevation] of tie-in exit (local coordinates).
        tie2_state: List [Easting, Northing, Elevation] of tie-in exit (State Plane coordinates).
        state_plane_zone: FIPS code for the State Plane coordinate system.

    Returns:
        Transformed DataFrame with State Plane and Latitude/Longitude coordinates.
    """
    # Debug: Print tie-in points
    print(f"Local Entry (tie1_local): {tie1_local}")
    print(f"State Plane Entry (tie1_state): {tie1_state}")
    print(f"Local Exit (tie2_local): {tie2_local}")
    print(f"State Plane Exit (tie2_state): {tie2_state}")
    print(f"DEBUG: state_plane_zone received: {state_plane_zone}")
    EPSG_Code = spcs83_to_epsg[state_plane_zone]
    print(f"DEBUG: EPSG_Code being used: {EPSG_Code}")

    # Step 1: Translation
    T_x = tie1_state[0] - tie1_local[0]
    T_y = tie1_state[1] - tie1_local[1]
    T_z = tie1_state[2] - tie1_local[2]

    data['Translated_X'] = data['Away'] + T_x
    data['Translated_Y'] = -data['Right'] + T_y
    data['Translated_Z'] = data['Elevation'] + T_z

    # Step 2: Calculate Rotation Angle
    delta_x = tie2_state[0] - tie1_state[0]
    delta_y = tie2_state[1] - tie1_state[1]
    theta = np.arctan2(delta_y, delta_x)  # Azimuth angle in radians

    # Rotate Points
    translated_x = data['Translated_X'] - tie1_state[0]
    translated_y = data['Translated_Y'] - tie1_state[1]

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    data['Rotated_X'] = cos_theta * translated_x - sin_theta * translated_y + tie1_state[0]
    data['Rotated_Y'] = sin_theta * translated_x + cos_theta * translated_y + tie1_state[1]
    data['Rotated_Z'] = data['Translated_Z']

    # Debug: Verify rotation step
    if 'Rotated_X' not in data.columns or 'Rotated_Y' not in data.columns:
        raise ValueError("Rotation failed. Missing 'Rotated_X' or 'Rotated_Y'.")
    print("Rotated Coordinates:")
    print(data[['Rotated_X', 'Rotated_Y', 'Rotated_Z']])

    # Step 3: Convert State Plane to Latitude/Longitude
    transformer_to_latlon = Transformer.from_crs(f"EPSG:{EPSG_Code}", "EPSG:4326", always_xy=True)

    print("DEBUG: Sample of Rotated_X before transform:")
    print(data['Rotated_X'].head())  # ADD THIS
    print("DEBUG: Sample of Rotated_Y before transform:")
    print(data['Rotated_Y'].head())  # ADD THIS

    data['Latitude'], data['Longitude'], data['Altitude'] = transformer_to_latlon.transform(
        data['Rotated_X'], data['Rotated_Y'], data['Rotated_Z']
    )

    # print("Latitude/Longitude Results:")
    # print(data[['Latitude','Longitude', 'Altitude']])

    return data
