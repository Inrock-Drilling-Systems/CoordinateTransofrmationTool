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
    # Debug: Print tie-in points
    print(f"Local Entry (tie1_local): {tie1_local}")
    print(f"State Plane Entry (tie1_state): {tie1_state}")
    print(f"Local Exit (tie2_local): {tie2_local}")
    print(f"State Plane Exit (tie2_state): {tie2_state}")

    EPSG_Code = spcs83_to_epsg[state_plane_zone]

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

    # Debug: Verify rotation step
    print("State Plane Coordinates:")
    print(data[['Easting', 'Northing', 'Elevation_TR']])

    # Step 3: Transform to Latitude/Longitude
    # Create CRS objects for more explicit control
    state_plane = CRS.from_epsg(EPSG_Code)
    wgs84 = CRS.from_epsg(4326)

    # Create transformer with explicit direction
    transformer_to_latlon = Transformer.from_crs(
        state_plane,
        wgs84,
        always_xy=True
    )

    # Transform coordinates
    longs, lats, alts = transformer_to_latlon.transform(
        data['Easting'],
        data['Northing'],
        data['Elevation_TR']
    )

    # Assign transformed coordinates
    data['Latitude'] = lats
    data['Longitude'] = longs
    data['Altitude'] = alts

    # Debug: Verify final coordinates
    print("Final Latitude/Longitude:")
    print(data[['Latitude', 'Longitude', 'Altitude']])

    # Clean up intermediate calculation columns
    data = data.drop(['Translated_X', 'Translated_Y', 'Translated_Z'], axis=1, errors='ignore')

    return data