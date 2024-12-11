from pyproj import Transformer

def test_transformer(state_plane_epsg, easting, northing, elevation):
    """
    Test the pyproj Transformer for a given input.

    Args:
        state_plane_epsg (int): EPSG code for the state plane system.
        easting (float): Easting (X) coordinate in the state plane system.
        northing (float): Northing (Y) coordinate in the state plane system.
        elevation (float): Elevation (Z) coordinate.

    Returns:
        tuple: (lat, lon, alt): Transformed latitude, longitude, and altitude.
    """
    transformer = Transformer.from_crs(f"EPSG:{state_plane_epsg}", "EPSG:4326", always_xy=True)
    lat, lon, alt = transformer.transform(easting, northing, elevation)
    return lat, lon, alt


# Define your test cases
def run_tests():
    test_cases = [
        {
            "state_plane_epsg": 3435,  # Illinois East (US Feet)
            "easting": 1148444.784,
            "northing": 1942198.698,
            "elevation": 100.0,
            "expected_lat": 41.997337,
            "expected_lon": -87.729287,
        },
        {
            "state_plane_epsg": 26971,  # Illinois East (meters)
            "easting": 350000,
            "northing": 1600000,
            "elevation": 30.0,
            "expected_lat": 39.830000,  # Replace with correct expected value
            "expected_lon": -88.000000,  # Replace with correct expected value
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"Running Test Case {i}...")
        lat, lon, alt = test_transformer(
            case["state_plane_epsg"],
            case["easting"],
            case["northing"],
            case["elevation"],
        )
        print(f"Input: {case}")
        print(f"Output: Latitude={lat}, Longitude={lon}, Altitude={alt}")
        print(f"Expected: Latitude={case['expected_lat']}, Longitude={case['expected_lon']}")
        print("---")

# Run the tests
if __name__ == "__main__":
    run_tests()
