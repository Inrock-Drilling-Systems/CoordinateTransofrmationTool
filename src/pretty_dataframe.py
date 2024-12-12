import pandas as pd

def correct_output(df):
    """
    Transforms a DataFrame by dropping columns, renaming columns, and swapping data points between two columns.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Consts:
        drop_columns (list): List of column names to drop.
        rename_columns (dict): Dictionary of columns to rename, where keys are old names and values are new names.
        swap_columns (tuple): Tuple of two column names (col1, col2) whose data points need to be swapped.

    Returns:
        pd.DataFrame: The transformed DataFrame.
    """

    drop_columns = [
        "Translated_X",
        "Translated_Y",
        "Translated_Z"
    ]

    rename_columns = {
        "Rotated_X": "Easting",
        "Rotated_Y": "Northing",
        "Rotated_Z": "Elevation_TR"
    }

    swap_columns = [
        "Latitude",
        "Longitude"
    ]

    # Drop specified columns
    df = df.drop(columns=drop_columns, errors='ignore')

    # Rename specified columns
    df = df.rename(columns=rename_columns)

    # Swap data points between the two specified columns
    col1, col2 = swap_columns
    if col1 in df.columns and col2 in df.columns:
        df[col1], df[col2] = df[col2], df[col1]

    return df
