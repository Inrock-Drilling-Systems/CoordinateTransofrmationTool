import folium

def create_map(latitudes, longitudes, elevations, units="ft"):
    """
    Creates a folium map with points based on given latitudes, longitudes, and elevations.

    Args:
        latitudes: Pandas Series of latitudes.
        longitudes: Pandas Series of longitudes.
        elevations: Pandas Series of elevations.
        units: String (default = USft)

    Returns:
        A folium.Map object.
    """
    # Center the map and determine zoom based on bounds
    bounds = [[latitudes.min(), longitudes.min()], [latitudes.max(), longitudes.max()]]
    map_center = [latitudes.mean(), longitudes.mean()]
    m = folium.Map(location=map_center, zoom_start=15)

    # Fit map to bounds
    m.fit_bounds(bounds)

    # Add points to the map
    for lat, lon, elev in zip(latitudes, longitudes, elevations):
        folium.Marker(
            [lat,lon],
            popup=f"Elevation: {elev} " + units,
            tooltip="Point"
        ).add_to(m)

    return m
