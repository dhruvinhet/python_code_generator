# main.py
import streamlit as st
import pandas as pd
from data_handler import load_car_data, save_car_data
from rental_logic import check_availability, calculate_rental_cost, record_rental

# Load car data from CSV file
DATA_FILE = 'car_data.csv'

# Function to display available cars
def display_available_cars(cars):
    st.header("Available Cars")
    if cars.empty:
        st.write("No cars available.")
    else:
        st.dataframe(cars)

# Function to handle rental request
def handle_rental_request(cars):
    st.header("Rental Request")

    if cars.empty:
        st.write("No cars available for rent.")
        return

    car_ids = cars['car_id'].tolist()
    selected_car_id = st.selectbox("Select a car to rent:", car_ids)
    rental_days = st.number_input("Enter the number of rental days:", min_value=1, step=1)

    if st.button("Request Rental"):
        selected_car = cars[cars['car_id'] == selected_car_id].iloc[0].to_dict()
        if not check_availability(selected_car):
            st.error("Car is not available.")
            return

        rental_cost = calculate_rental_cost(selected_car, rental_days)
        st.write(f"Rental cost: ${rental_cost}")

        if st.button("Confirm Rental"):
            try:
                record_rental(selected_car['car_id'], rental_days, DATA_FILE)
                st.success("Rental confirmed!")
                # Refresh the data and UI
                cars = load_car_data(DATA_FILE)
                display_available_cars(cars)
            except Exception as e:
                st.error(f"Error recording rental: {e}")


# Function to display rental history
def display_rental_history():
    st.header("Rental History")
    try:
        rentals = pd.read_csv('rental_history.csv')
        st.dataframe(rentals)
    except FileNotFoundError:
        st.write("No rental history available.")
    except Exception as e:
        st.error(f"Error loading rental history: {e}")

# Main function
def main():
    st.title("Car Rental App")

    # Load car data
    try:
        cars = load_car_data(DATA_FILE)
    except FileNotFoundError:
        st.error("Car data file not found. Please create car_data.csv.")
        return
    except Exception as e:
        st.error(f"Error loading car data: {e}")
        return

    # Display available cars
    display_available_cars(cars)

    # Handle rental request
    handle_rental_request(cars)

    # Display rental history
    display_rental_history()

# Run the app
if __name__ == "__main__":
    main()