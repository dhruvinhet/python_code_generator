import pandas as pd
from config import DATA_PATH

def load_data():
    """Loads the dataset from the specified path."""
    try:
        df = pd.read_csv(DATA_PATH)
        # Add basic data validation here.  Since schema is unknown, a simple check will suffice.
        if df.empty:
            raise ValueError("Dataset is empty.")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found at {DATA_PATH}")
    except pd.errors.EmptyDataError:
        raise ValueError("Dataset file is empty.")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing dataset file: {e}")