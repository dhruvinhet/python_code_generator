import pandas as pd
import logging
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data(filepath):
    """Loads data from CSV, JSON, or Excel files.

    Args:
        filepath (str): Path to the data file.

    Returns:
        pandas.DataFrame: The loaded data as a pandas DataFrame.  Returns None if file loading fails.
    """
    try:
        _, file_extension = os.path.splitext(filepath)
        logging.info(f"Loading data from {filepath}")
        if file_extension.lower() == '.csv':
            df = pd.read_csv(filepath)
        elif file_extension.lower() == '.json':
            with open(filepath, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        elif file_extension.lower() == '.xlsx' or file_extension.lower() == '.xls':
            df = pd.read_excel(filepath)
        else:
            logging.error(f"Unsupported file format: {file_extension}")
            return None
        logging.info(f"Data loaded successfully. Shape: {df.shape}")
        return df
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return None
    except pd.errors.EmptyDataError:
        logging.error(f"Empty data file: {filepath}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while loading data: {e}")
        return None