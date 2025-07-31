# rental_logic.py
import datetime
import pandas as pd

RENTAL_HISTORY_FILE = 'rental_history.csv'

# Function to check car availability
def check_availability(car):
    # Implement your availability check logic here
    # For simplicity, we assume a car is always available
    return car['is_available']

# Function to calculate rental cost
def calculate_rental_cost(car, rental_days):
    daily_rate = car['daily_rate']
    rental_cost = daily_rate * rental_days
    return rental_cost

# Function to record rental
def record_rental(car_id, rental_days, car_data_file):
    try:
        # Load car data to get car details
        cars = pd.read_csv(car_data_file)
        car = cars[cars['car_id'] == car_id].iloc[0].to_dict()

        # Create rental record
        rental_data = {
            'car_id': car['car_id'],
            'model': car['model'],
            'rental_date': datetime.date.today().strftime('%Y-%m-%d'),
            'rental_days': rental_days,
            'daily_rate': car['daily_rate'],
            'total_cost': calculate_rental_cost(car, rental_days)
        }

        rental_df = pd.DataFrame([rental_data])

        # Append rental data to rental history CSV
        try:
            existing_rentals = pd.read_csv(RENTAL_HISTORY_FILE)
            rental_df = pd.concat([existing_rentals, rental_df], ignore_index=True)
        except FileNotFoundError:
            pass  # It's the first rental, so create a new file

        rental_df.to_csv(RENTAL_HISTORY_FILE, index=False)

        # Update car availability (set to False)
        cars.loc[cars['car_id'] == car_id, 'is_available'] = False
        cars.to_csv(car_data_file, index=False)

    except Exception as e:
        print(f"Error recording rental: {e}")