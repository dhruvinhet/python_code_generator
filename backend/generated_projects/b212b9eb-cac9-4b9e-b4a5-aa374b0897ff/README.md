# Car Rental Application

A Streamlit-based car rental management system that allows users to view available cars, make rental requests, and track rental history.

## Features

- **View Available Cars**: Display all cars that are currently available for rent
- **Rental Request**: Select a car and specify rental duration to calculate costs
- **Rental Confirmation**: Complete the rental process and update car availability
- **Rental History**: View all past rentals with details

## Files Description

- **`main.py`**: Main Streamlit application with user interface
- **`rental_logic.py`**: Core rental business logic and calculations
- **`data_handler.py`**: Data management functions for CSV operations
- **`car_data.csv`**: Database of available cars with pricing
- **`rental_history.csv`**: Record of all completed rentals

## Data Structure

### Car Data (`car_data.csv`)
- `car_id`: Unique identifier for each car
- `model`: Car model name
- `daily_rate`: Cost per day in USD
- `is_available`: Boolean indicating if car is available for rent

### Rental History (`rental_history.csv`)
- `car_id`: ID of the rented car
- `model`: Car model name
- `rental_date`: Date when rental was made (YYYY-MM-DD)
- `rental_days`: Number of days for the rental
- `daily_rate`: Daily rate at time of rental
- `total_cost`: Total cost calculated (daily_rate × rental_days)

## How to Run

1. Make sure you have the required dependencies:
   ```bash
   pip install streamlit pandas
   ```

2. Run the application:
   ```bash
   streamlit run main.py
   ```

3. Open your web browser and navigate to the provided URL (usually http://localhost:8501)

## Using the Application

1. **View Cars**: The main page shows all available cars with their details
2. **Make a Rental**: 
   - Select a car from the dropdown
   - Enter the number of rental days
   - Click "Request Rental" to see the cost
   - Click "Confirm Rental" to complete the transaction
3. **Check History**: Scroll down to see all past rentals

## Sample Data

The application comes pre-loaded with 15 sample cars including:
- Economy cars (Honda Civic, Nissan Altima)
- Mid-range cars (Toyota Camry, Mazda CX-5)
- Luxury cars (BMW 3 Series, Mercedes C-Class)
- Electric car (Tesla Model 3)

## Notes

- When a car is rented, its availability is automatically set to `False`
- Rental history is automatically updated with each transaction
- The system prevents renting unavailable cars
- All data is stored in CSV files for persistence

## Troubleshooting

- If you get a "Car data file not found" error, ensure `car_data.csv` exists in the same directory
- If rental history doesn't display, the `rental_history.csv` file will be created automatically on the first rental
