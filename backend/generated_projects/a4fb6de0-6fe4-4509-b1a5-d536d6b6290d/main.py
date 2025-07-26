# main.py
import streamlit as st
import math
import numpy as np
import calculator_logic
import ui_components


# Main application function
def main():
    st.title("Scientific Calculator")

    # Create input fields using the function from ui_components.py
    num1, num2, operation = ui_components.create_input_fields()

    # Create button layout
    calculate_button = ui_components.create_button_layout()

    # Perform calculation when the button is clicked
    if calculate_button:
        if operation:
            try:
                result = calculate(num1, num2, operation)
                display_result(result)
            except ValueError as e:
                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please select an operation.")


# Function to perform calculations based on the selected operation
def calculate(num1, num2, operation):
    try:
        num1 = float(num1) if num1 else 0.0
        num2 = float(num2) if num2 else 0.0
    except ValueError:
        raise ValueError("Invalid input for numbers.")

    if operation == "Add":
        return calculator_logic.add(num1, num2)
    elif operation == "Subtract":
        return calculator_logic.subtract(num1, num2)
    elif operation == "Multiply":
        return calculator_logic.multiply(num1, num2)
    elif operation == "Divide":
        try:
            return calculator_logic.divide(num1, num2)
        except ValueError as e:
            raise e
    elif operation == "Power":
        return calculator_logic.power(num1, num2)
    elif operation == "Square Root (num1)":
        if num1 < 0:
            raise ValueError("Cannot calculate square root of a negative number.")
        return calculator_logic.square_root(num1)
    elif operation == "Sin (num1)":
        return calculator_logic.sin(num1)
    elif operation == "Cos (num1)":
        return calculator_logic.cos(num1)
    elif operation == "Tan (num1)":
        return calculator_logic.tan(num1)
    elif operation == "Log (num1)":
        if num1 <= 0:
            raise ValueError("Cannot calculate log of a non-positive number.")
        return calculator_logic.log(num1)
    elif operation == "Factorial (num1)":
        if not float(num1).is_integer() or float(num1) < 0:
            raise ValueError("Cannot calculate factorial of a non-negative integer.")
        return calculator_logic.factorial(int(num1))
    else:
        raise ValueError("Invalid operation")


# Function to display the result
def display_result(result):
    st.success(f"Result: {result}")


# Run the Streamlit application
if __name__ == "__main__":
    main()
