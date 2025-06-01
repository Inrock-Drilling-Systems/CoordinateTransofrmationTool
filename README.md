# 3D Coordinate Transformation Tool

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-streamlit-share-link.streamlit.app/)

## Overview

Welcome to the **Inrock Transformation Tool**! This Streamlit-powered web application simplifies the process of converting 3D coordinates between different systems, primarily focusing on local coordinates and State Plane Coordinate Systems (SPCS). It's designed to assist surveyors, engineers, and geospatial professionals in managing and transforming their data.

This tool now supports a multi-page interface, offering dedicated sections for coordinate transformation and State Plane zone lookups.

## Features

* **3D Coordinate Transformation:** Convert survey data (Away, Right, Elevation) from a local coordinate system to a selected State Plane Coordinate System (SPCS).
* **Tie-in Point Management:** Easily input and manage local and State Plane tie-in points for accurate transformations.
* **Horizontal Span Calculation:** Automatically calculate and display horizontal spans for both local and State Plane coordinates.
* **State Plane Zone Lookup:**
    * **By State & Zone Name:** Find State Plane Zone FIPS codes and corresponding EPSG codes by selecting a U.S. State and a specific zone.
    * **By Latitude/Longitude:** (Conceptual - Requires spatial data integration) Determine the SPCS zone based on geographic coordinates.
* **CSV Upload & Processing:** Upload CSV files containing local survey data for batch transformation.
* **Transformed Data Download:** Download transformed coordinates as a CSV file.
* **Map Visualization:** Overlay transformed coordinates on an interactive map (requires Latitude, Longitude, and Altitude in the output).
* **KMZ Output:** Generate KMZ files for easy visualization of transformed points in geospatial software like Google Earth.

## Getting Started

Follow these steps to set up and run the 3D Coordinate Transformation Tool on your local machine.

### Prerequisites

Make sure you have Python 3.8+ installed.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/Inrock-Drilling-Systems/CoordinateTransofrmationTool.git](https://github.com/Inrock-Drilling-Systems/CoordinateTransofrmationTool.git)
    cd CoordinateTransofrmationTool
    ```

2.  **Create a virtual environment** (highly recommended):

    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**

    * **macOS / Linux:**
        ```bash
        source .venv/bin/activate
        ```
    * **Windows:**
        ```bash
        .venv\Scripts\activate
        ```

4.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    * **Note:** If you encounter issues with `geopandas`, `fiona`, or `shapely` during installation, you might need to install their underlying geospatial libraries (GDAL, GEOS, PROJ) separately. Refer to their official documentation for platform-specific instructions if `pip` fails.

### Running the Application

Once all dependencies are installed, you can run the Streamlit application from the root directory of the repository:

```bash
streamlit run app.py
```

Usage
The application opens to a welcome page. Use the sidebar on the left to navigate between the different functionalities:

```bash
Coordinate Converter: This is the main transformation tool where you input tie-in points, upload your survey data, and perform transformations.
State Plane Lookup: Use this page to find information about State Plane Coordinate System zones.
Project Structure
CoordinateTransofrmationTool/
├── .github/
├── .streamlit/             # Streamlit configuration (e.g., secrets, config)
├── pages/
│   ├── 1_CoordConverter.py # Main 3D Coordinate Transformation page
│   └── 2_State_Plane_Lookup.py # State Plane Zone Lookup page
├── src/                    # Contains core Python scripts and utility functions
│   ├── __init__.py         # Makes 'src' a Python package
│   ├── constants.py        # Stores EPSG codes, FIPS codes, and state/zone mappings
│   ├── create_map.py       # Handles map visualization logic
│   ├── generate_kmz.py     # Functions for KMZ file generation
│   ├── pretty_dataframe.py # Utilities for formatting dataframes
│   ├── remove_and_reformat.py # Processes and reformats survey CSVs
│   └── transformations.py  # Core coordinate transformation logic
├── .gitignore              # Specifies intentionally untracked files to ignore
├── app.py                  # Main entry point for the Streamlit application
├── requirements.txt        # Lists Python dependencies
└── README.md               # Project overview and instructions
```

Contributing
We welcome contributions to improve this tool! If you have suggestions, bug reports, or want to contribute code, please open an issue or submit a pull request on the GitHub repository.

License
MIT License

Contact
For questions or support, please open an issue on the GitHub repository.