import simplekml

def generate_kmz(latitudes, longitudes, elevations, descriptions, output_file="output.kmz"):
    """
    Generates a KMZ file from latitude, longitude, and elevation data.

    Args:
        latitudes: List or Pandas Series of latitude values.
        longitudes: List or Pandas Series of longitude values.
        elevations: List or Pandas Series of elevation values.
        descriptions: List or Pandas Series of descriptions values
        output_file: Name of the output KMZ file.

    Returns:
        Path to the generated KMZ file.
    """
    kml = simplekml.Kml()
    icon_url = "https://maps.google.com/mapfiles/kml/pal4/icon49.png"

    # # Iterate over the data to create placemarks
    # for lat, lon, elev, desc in zip(latitudes, longitudes, elevations, descriptions):
    #     pnt = kml.newpoint(description=desc, coords=[(lon, lat)])
    #     pnt.style.iconstyle.icon.href = icon_url
    #     pnt.style.iconstyle.scale = 1.5  # Adjust the scale of the icon as needed

    # Add points to the KML file
    for lat, lon, elev, desc in zip(latitudes, longitudes, elevations, descriptions):
        pnt = kml.newpoint(name="",description=desc, coords=[(lat, lon, elev)])  # (longitude, latitude, elevation, descriptions)
        pnt.style.iconstyle.icon.href = icon_url
        pnt.style.iconstyle.scale = 1.5

    # Save as KMZ
    kml.savekmz(output_file)
    return output_file
