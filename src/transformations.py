import numpy as np
from pyproj import Transformer
from src.constants import spcs83_to_epsg


def usft_to_meters(value):
    """Convert US Survey Feet to Meters"""
    return value * 0.3048


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
    # Debug: Print tie-in points and convert State Plane coordinates from US feet to meters
    print(f"Local Entry (tie1_local): {tie1_local}")
    # Swap Easting/Northing and convert to meters for state plane coordinates
    tie1_state_meters = [usft_to_meters(tie1_state[1]), usft_to_meters(tie1_state[0]), usft_to_meters(tie1_state[2])]
    tie2_state_meters = [usft_to_meters(tie2_state[1]), usft_to_meters(tie2_state[0]), usft_to_meters(tie2_state[2])]

    print(f"State Plane Entry (meters): {tie1_state_meters}")
    print(f"Local Exit (tie2_local): {tie2_local}")
    print(f"State Plane Exit (meters): {tie2_state_meters}")

    EPSG_Code = spcs83_to_epsg[state_plane_zone]

    # Step 1: Translation (using meter-converted coordinates)
    T_x = tie1_state_meters[0] - tie1_local[0]
    T_y = tie1_state_meters[1] - tie1_local[1]
    T_z = tie1_state_meters[2] - tie1_local[2]

    data['Translated_X'] = data['Away'] + T_x
    data['Translated_Y'] = -data['Right'] + T_y
    data['Translated_Z'] = data['Elevation'] + T_z

    # Step 2: Calculate Rotation Angle using meter-converted coordinates
    delta_x = tie2_state_meters[0] - tie1_state_meters[0]
    delta_y = tie2_state_meters[1] - tie1_state_meters[1]
    theta = np.arctan2(delta_y, delta_x)  # Azimuth angle in radians

    # Rotate Points
    translated_x = data['Translated_X'] - tie1_state_meters[0]
    translated_y = data['Translated_Y'] - tie1_state_meters[1]

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    data['Rotated_X'] = cos_theta * translated_x - sin_theta * translated_y + tie1_state_meters[0]
    data['Rotated_Y'] = sin_theta * translated_x + cos_theta * translated_y + tie1_state_meters[1]
    data['Rotated_Z'] = data['Translated_Z']

    # Debug: Verify rotation step
    if 'Rotated_X' not in data.columns or 'Rotated_Y' not in data.columns:
        raise ValueError("Rotation failed. Missing 'Rotated_X' or 'Rotated_Y'.")
    print("Rotated Coordinates (meters):")
    print(data[['Rotated_X', 'Rotated_Y', 'Rotated_Z']])

    # Step 3: Transform to Latitude/Longitude
    # Note: Using always_xy=True ensures correct handling of coordinate order
    transformer_to_latlon = Transformer.from_crs(f"EPSG:{EPSG_Code}", "EPSG:4326", always_xy=True)
    data['Latitude'], data['Longitude'], data['Altitude'] = transformer_to_latlon.transform(
        data['Rotated_Y'],  # Swap X/Y for correct E/N orientation
        data['Rotated_X'],
        data['Rotated_Z']
    )

    # Store the meter-converted State Plane coordinates
    data['Easting'] = data['Rotated_Y']  # Store final coordinates in correct orientation
    data['Northing'] = data['Rotated_X']
    data['Elevation_TR'] = data['Rotated_Z']

    # Debug: Verify final coordinates
    print("Final Latitude/Longitude:")
    print(data[['Latitude', 'Longitude', 'Altitude']])

    return data