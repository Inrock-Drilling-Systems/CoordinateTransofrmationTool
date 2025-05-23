import pandas as pd

def process_survey_csv(file_input):
    """
    Process a survey CSV file or file-like object to extract the table and transform it into the target format.

    Parameters:
        file_input (str or file-like object): Path to the original CSV file or file-like object.

    Returns:
        pd.DataFrame: Transformed dataframe matching the target format.
    """
    # Read the raw file content
    if isinstance(file_input, str):
        with open(file_input, 'r') as file:
            raw_text = file.readlines()
    else:
        raw_text = file_input.read().decode('utf-8').splitlines()

    # Debugging: Print lines containing any keyword
    header_keywords = ['Joint', 'MD', 'Incl', 'Az', 'Away', 'Elev', 'Right']
    matching_lines = [
        (i, line) for i, line in enumerate(raw_text)
        if any(keyword in line for keyword in header_keywords)
    ]

    print("Matching Lines for Debugging:")
    for idx, content in matching_lines:
        print(f"Line {idx}: {content}")

    # Locate the header and extract table rows
    try:
        header_index = next(
            i for i, line in enumerate(raw_text)
            if all(keyword in line for keyword in header_keywords)
        )
    except StopIteration:
        raise ValueError(
            f"Header containing key terms {header_keywords} not found in the file."
        )
    table_data = raw_text[header_index:]

    # Split the header and data into separate components
    header = table_data[0].strip().strip(',').split(',')  # Remove trailing commas and split
    data_rows = [row.strip().strip(',').split(',') for row in table_data[1:]]

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data_rows, columns=header)

    # Transform the data to match the target format
    df = df.rename(columns={"Joint": "Point", "Elev": "Elevation"})
    df = df[["Point", "Away", "Right", "Elevation"]]  # Select required columns

    # Convert types to numeric where applicable
    for col in ["Away", "Right", "Elevation"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Add a Description column
    def generate_description(row):
        if row["Point"] == "(entry)":
            return "(entry)"
        return f"JT {row['Point']}"

    df["Description"] = df.apply(generate_description, axis=1)

    # Convert "Point" to a sequential numeric index
    df["Point"] = range(1, len(df) + 1)

    return df
