import pandas as pd

def load_data(filepath):
    """Loads data from a specified filepath.  Handles CSV and Excel files."""
    try:
        if filepath.lower().endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported file type: {filepath}")
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        print(f"Error parsing file {filepath}: {e}")
        return None
    except ValueError as e:
        print(e)
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading data: {e}")
        return None