import pandas as pd
import os
from config import DATA_PATH

def load_data():
    try:
        data = pd.read_csv(DATA_PATH)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found at {DATA_PATH}")
    except pd.errors.EmptyDataError:
        raise ValueError("Dataset file is empty.")
    except pd.errors.ParserError:
        raise ValueError("Error parsing dataset file.")

def get_data_stats(data=None):
    if data is None:
        data = load_data()
    stats = data.describe()
    return stats

def preview_data(rows=10, data=None):
    if data is None:
        data = load_data()
    return data.head(rows).to_dict(orient='records')