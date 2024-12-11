import simplekml

def generate_kmz(latitudes, longitudes, elevations, output_file="output.kmz"):
    """
    Generates a KMZ file from latitude, longitude, and elevation data.

    Args:
        latitudes: List or Pandas Series of latitude values.
        longitudes: List or Pandas Series of longitude values.
        elevations: List or Pandas Series of elevation values.
        output_file: Name of the output KMZ file.

    Returns:
        Path to the generated KMZ file.
    """
    kml = simplekml.Kml()

    # Add points to the KML file
    for lat, lon, elev in zip(latitudes, longitudes, elevations):
        kml.newpoint(name="Point", coords=[(lon, lat, elev)])  # (longitude, latitude, elevation)

    # Save as KMZ
    kml.savekmz(output_file)
    return output_file

