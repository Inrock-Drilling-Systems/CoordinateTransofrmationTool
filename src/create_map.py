import folium

def create_map(latitudes, longitudes, elevations):
    """
    Creates a folium map with points based on given latitudes, longitudes, and elevations.

    Args:
        latitudes: Pandas Series of latitudes.
        longitudes: Pandas Series of longitudes.
        elevations: Pandas Series of elevations.

    Returns:
        A folium.Map object.
    """
    # Center the map and determine zoom based on bounds
    bounds = [[longitudes.min(), latitudes.min()], [longitudes.max(), latitudes.max()]]
    map_center = [longitudes.mean(), latitudes.mean()]
    m = folium.Map(location=map_center, zoom_start=15)

    # Fit map to bounds
    m.fit_bounds(bounds)

    # Add points to the map
    for lat, lon, elev in zip(latitudes, longitudes, elevations):
        folium.Marker(
            [lon,lat],
            popup=f"Elevation: {elev} m",
            tooltip="Point"
        ).add_to(m)

    return m
