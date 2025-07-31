# utils.py
import pandas as pd


def load_data(filepath):
    """Loads data from a CSV file using Pandas."""
    try:
        data = pd.read_csv(filepath)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def save_data(data, filepath):
    """Saves data to a CSV file using Pandas."""
    try:
        data.to_csv(filepath, index=False)
        print(f"Data saved successfully to {filepath}")
    except Exception as e):
        print(f"An error occurred: {e}")