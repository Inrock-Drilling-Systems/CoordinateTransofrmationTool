import pytest
from pyproj import Transformer

def test_transformer(state_plane_epsg, easting, northing, elevation):
    transformer = Transformer.from_crs(f"EPSG:{state_plane_epsg}", "EPSG:4326", always_xy=True)
    lat, lon, alt = transformer.transform(easting, northing, elevation)
    return lat, lon, alt

@pytest.mark.parametrize("epsg,easting,northing,elevation,expected_lat,expected_lon", [
    (3435, 1148444.784, 1942198.698, 100.0, 41.997337, -87.729287),  # Illinois East (US Feet)
    (26971, 350000, 1600000, 30.0, 39.830000, -88.000000),  # Illinois East (Meters)
])
def test_coordinate_transformation(epsg, easting, northing, elevation, expected_lat, expected_lon):
    lat, lon, _ = test_transformer(epsg, easting, northing, elevation)
    assert pytest.approx(lat, 0.0001) == expected_lat, f"Latitude mismatch for EPSG {epsg}"
    assert pytest.approx(lon, 0.0001) == expected_lon, f"Longitude mismatch for EPSG {epsg}"
