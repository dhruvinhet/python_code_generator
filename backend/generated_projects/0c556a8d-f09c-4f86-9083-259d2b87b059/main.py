# main.py
import streamlit as st
import pandas as pd
from data_loader import load_car_data
from utils import calculate_rental_cost, validate_date_input
import datetime

# Load car data
try:
    car_data = load_car_data("car_data.csv")  # Assuming car_data.csv exists
    if car_data.empty:
        st.error("Car data could not be loaded. Please check the data file.")
except Exception as e:
    st.error(f"An error occurred while loading car data: {e}")
    car_data = pd.DataFrame() # Ensure car_data is always a DataFrame

# Function to display the list of cars
def display_car_list(df):
    """Displays the car list in a Streamlit dataframe."""
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No car data to display.")

# Function to display rental details and calculate cost
def display_rental_details(df):
    """Displays rental details and calculates the cost.

    Args:
        df (pd.DataFrame): The car data DataFrame.
    """
    st.header("Rental Details")

    if df.empty:
        st.warning("No car data available to display rental details.")
        return

    car_names = df['model'].tolist()
    if not car_names:
        st.warning("No car models found in the data.")
        return

    selected_car = st.selectbox("Select a car:", car_names)

    # Find the price per day for the selected car
    try:
        price_per_day = df[df['model'] == selected_car]['price_per_day'].iloc[0]
    except IndexError:
        st.error(f"Price per day not found for car: {selected_car}")
        return
    except KeyError:
        st.error("The 'price_per_day' column is missing in the car data.")
        return

    start_date = st.date_input("Start Date", datetime.date.today())
    end_date = st.date_input("End Date", datetime.date.today() + datetime.timedelta(days=7))

    # Validate the dates
    if not validate_date_input(start_date, end_date):
        st.error("End date must be after start date.")
        return

    # Calculate rental days
    rental_days = (end_date - start_date).days

    # Calculate rental cost
    total_cost = calculate_rental_cost(price_per_day, rental_days)

    st.write(f"You selected: {selected_car}")
    st.write(f"Start Date: {start_date}")
    st.write(f"End Date: {end_date}")
    st.write(f"Rental Days: {rental_days}")
    st.write(f"Price per day: ${price_per_day:.2f}")
    st.write(f"Total Rental Cost: ${total_cost:.2f}")


# Main function
def main():
    """Main function to run the Streamlit application."""
    st.title("Car Rental App")
    st.write("Welcome to the Car Rental App!")

    display_car_list(car_data)
    display_rental_details(car_data)

# Run the Streamlit app
if __name__ == "__main__":
    main()