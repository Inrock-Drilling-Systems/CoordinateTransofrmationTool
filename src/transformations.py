import numpy as np
from pyproj import Transformer, CRS
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
    print(f"Local Entry (tie1_local): {tie1_local}")
    print(f"State Plane Entry (tie1_state): {tie1_state}")
    print(f"Local Exit (tie2_local): {tie2_local}")
    print(f"State Plane Exit (tie2_state): {tie2_state}")

    EPSG_Code = spcs83_to_epsg[state_plane_zone]
    print(f"Using EPSG code: {EPSG_Code}")

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

    # Store rotated coordinates directly in final columns
    data['Easting'] = cos_theta * translated_x - sin_theta * translated_y + tie1_state[0]
    data['Northing'] = sin_theta * translated_x + cos_theta * translated_y + tie1_state[1]
    data['Elevation_TR'] = data['Translated_Z']

    print("State Plane Coordinates (before transformation):")
    print(data[['Easting', 'Northing', 'Elevation_TR']].head())

    # Step 3: Transform to Latitude/Longitude using pipeline approach
    transformer_to_latlon = Transformer.from_crs(
        f"EPSG:{EPSG_Code}",
        "EPSG:4326",
        always_xy=True
    ).transform

    # Transform each point individually to maintain correct order
    lat_long_results = [
        transformer_to_latlon(easting, northing, elev)
        for easting, northing, elev in zip(
            data['Easting'],
            data['Northing'],
            data['Elevation_TR']
        )
    ]

    # Unpack results
    data['Longitude'], data['Latitude'], data['Altitude'] = zip(*lat_long_results)

    print("\nTransformation complete!")
    print("Sample of transformed coordinates:")
    print(data[['Easting', 'Northing', 'Latitude', 'Longitude']].head())

    # Clean up intermediate calculation columns
    data = data.drop(['Translated_X', 'Translated_Y', 'Translated_Z'], axis=1, errors='ignore')

    return data