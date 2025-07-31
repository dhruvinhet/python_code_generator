# utils.py
import datetime

def calculate_rental_cost(price_per_day, rental_days):
    """Calculates the total rental cost.

    Args:
        price_per_day (float): The price per day for the car.
        rental_days (int): The number of rental days.

    Returns:
        float: The total rental cost.
    """
    try:
        price_per_day = float(price_per_day)
        rental_days = int(rental_days)
        if price_per_day < 0 or rental_days < 0:
            return 0.0  # Handle negative inputs
        return price_per_day * rental_days
    except ValueError:
        return 0.0 # Handle cases with invalid input

def validate_date_input(start_date, end_date):
    """Validates that the end date is after the start date.

    Args:
        start_date (datetime.date): The start date.
        end_date (datetime.date): The end date.

    Returns:
        bool: True if the end date is after the start date, False otherwise.
    """
    return end_date > start_date

# Example Usage:
if __name__ == '__main__':
    # Testing the utility functions
    price = 50.0
    days = 7
    cost = calculate_rental_cost(price, days)
    print(f"Rental cost for {days} days at ${price} per day: ${cost}")

    start = datetime.date(2024, 1, 1)
    end = datetime.date(2024, 1, 8)
    is_valid = validate_date_input(start, end)
    print(f"Is end date after start date? {is_valid}")