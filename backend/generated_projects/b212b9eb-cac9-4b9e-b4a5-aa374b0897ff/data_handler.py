# data_handler.py
import pandas as pd

# CSV file to store car data
DATA_FILE = 'car_data.csv'

# Function to load car data from CSV
def load_car_data(file_path):
    try:
        cars = pd.read_csv(file_path)
        return cars
    except FileNotFoundError:
        #Return empty DataFrame if file not found to prevent the program from crashing
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

# Function to save car data to CSV
def save_car_data(cars, file_path):
    try:
        cars.to_csv(file_path, index=False)
    except Exception as e:
        print(f"Error saving data: {e}")

# Function to add a new car
def add_car(car_data):
    try:
        cars = load_car_data(DATA_FILE)
        new_car = pd.DataFrame([car_data])
        cars = pd.concat([cars, new_car], ignore_index=True)
        save_car_data(cars, DATA_FILE)
    except Exception as e:
        print(f"Error adding car: {e}")

# Function to remove a car
def remove_car(car_id):
    try:
        cars = load_car_data(DATA_FILE)
        cars = cars[cars['car_id'] != car_id]
        save_car_data(cars, DATA_FILE)
    except Exception as e:
        print(f"Error removing car: {e}")