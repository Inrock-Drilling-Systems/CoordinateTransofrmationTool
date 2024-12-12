# Inrock Coordinate Converter

## Description
The Inrock Coordinate Converter is a tool designed to transform coordinates from an abstract local coordinate system to both the State Plane Coordinate System (CONUS) and WGS84 (Latitude/Longitude in decimal degrees). It utilizes "tie-in points" projected along a reference coordinate system to accurately convert localized coordinates, ensuring precise geospatial data representation.

## Features
- Import user coordinates via text fields or CSV upload
- Select the appropriate coordinate system for conversion
- Analyze both the original and transformed data
- View a map overview of the transformed points
- Download the transformed data in CSV or KMZ format for use in applications like Google Earth

## Installation
1. Ensure you have an internet browser and internet access.
2. Visit Inrock Coordinate Converter to access the applet.
3. Input properly configured data to use the tool effectively.

## Usage

To run locally, access directory from Command Prompt in the local app directory and run:

```
> pip install -r requirements.txt

.
.
.

> streamlit run coord_converter_app.py
```
Browser will open to ```localhost:8501``` where you can directly test any configuration changes in real-time.

To allow access to others on the same network, generate an Inbound Rule for your firewall for ```Port:8501``` and
provide your IPv4 address to another computer on your network to access the applet at ```your.ip.add.ress:8501``` from 
an internet browser.

If you do not know your IPv4 address, enter the following into Command Prompt:


```ipconfig -all```

### Use Case 1: End of Project Folder Submissions
- Utilize the tool to convert project coordinates for final submissions to clients.
- Ensure all data is accurately transformed and presented in the required formats (CSV or KMZ).

### Use Case 2: Real-Time Location Assistance
- Use the map overview feature to track the real-time location of the bit in reference to other points (such as IRs).
- Access the tool from your mobile phone for on-the-go geospatial data analysis.

## Contributing
We welcome contributions to the Inrock Coordinate Converter project! Here are some guidelines to help you get started:

### Reporting Issues
- If you encounter any bugs or have suggestions for improvements, please open an issue on our GitHub repository.

### Submitting Pull Requests
- Fork the repository and create a new branch for your feature or bug fix.
- Ensure your code follows our coding standards and best practices.
- Submit a pull request with a clear description of your changes and the problem they solve.

### Coding Standards
- Follow the PEP 8 style guide for Python code.
- Write clear, concise commit messages.
- Include comments and documentation for any new features or significant changes.

## License
This project is licensed under the MIT License.