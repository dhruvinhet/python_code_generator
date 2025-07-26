# src/user_interface.py

# This module defines the user interface using Streamlit and handles user interactions.

import streamlit as st
import calculator_logic


def main():
    """Main function to run the Streamlit application."""

    st.title("Scientific Calculator")

    # Input fields
    st.sidebar.header("Inputs")
    operation = st.sidebar.selectbox(
        "Select operation:",
        [
            "Add",
            "Subtract",
            "Multiply",
            "Divide",
            "Power",
            "Square Root",
            "Logarithm (base 10)",
            "Sine",
            "Cosine",
            "Tangent",
            "Factorial",
            "Degrees to Radians",
            "Radians to Degrees",
            "Natural Logarithm",
            "Exponent",
        ],
    )

    num1 = st.sidebar.number_input("Enter first number:", value=0.0)
    # Setting a default value for num2 to avoid errors with single-argument functions.
    num2 = st.sidebar.number_input("Enter second number (if applicable):")

    # Perform calculation based on selected operation
    result = None
    try:
        if operation == "Add":
            result = calculator_logic.add(num1, num2)
        elif operation == "Subtract":
            result = calculator_logic.subtract(num1, num2)
        elif operation == "Multiply":
            result = calculator_logic.multiply(num1, num2)
        elif operation == "Divide":
            result = calculator_logic.divide(num1, num2)
        elif operation == "Power":
            result = calculator_logic.power(num1, num2)
        elif operation == "Square Root":
            result = calculator_logic.square_root(num1)
        elif operation == "Logarithm (base 10)":
            result = calculator_logic.logarithm(num1)
        elif operation == "Sine":
            result = calculator_logic.sine(num1)
        elif operation == "Cosine":
            result = calculator_logic.cosine(num1)
        elif operation == "Tangent":
            result = calculator_logic.tangent(num1)
        elif operation == "Factorial":
            # Ensure the input is a non-negative integer for factorial.
            if num1 < 0:
                raise ValueError("Factorial is not defined for negative numbers")
            result = calculator_logic.factorial(int(num1))
        elif operation == "Degrees to Radians":
            result = calculator_logic.degrees_to_radians(num1)
        elif operation == "Radians to Degrees":
            result = calculator_logic.radians_to_degrees(num1)
        elif operation == "Natural Logarithm":
            result = calculator_logic.natural_logarithm(num1)
        elif operation == "Exponent":
            result = calculator_logic.exponent(num1)

    except ValueError as e:
        st.error(f"Error: {e}")
    except ZeroDivisionError as e:
        st.error(f"Error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

    # Display the result
    if result is not None:
        st.success(f"Result: {result}")


if __name__ == "__main__":
    main()
