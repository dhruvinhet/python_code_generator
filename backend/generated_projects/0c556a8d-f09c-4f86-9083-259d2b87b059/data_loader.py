# data_loader.py
import pandas as pd

def load_car_data(file_path):
    """Loads car data from a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The car data as a Pandas DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return pd.DataFrame()  # Return an empty DataFrame
    except pd.errors.EmptyDataError:
        print(f"Error: The file at {file_path} is empty.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

# Example usage (for demonstration purposes only. The actual csv file should be used in main.py.)
if __name__ == '__main__':
    # Create a dummy CSV file for demonstration
    data = {
        'model': ['Toyota Camry', 'Honda Civic', 'Ford Mustang'],
        'year': [2020, 2021, 2022],
        'price_per_day': [50, 45, 75]
    }
    df = pd.DataFrame(data)
    df.to_csv('car_data.csv', index=False)

    # Load the data
    car_data = load_car_data('car_data.csv')
    print(car_data)