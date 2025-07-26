# ui_components.py
import streamlit as st


# Function to create input fields for numbers and operation selection
def create_input_fields():
    col1, col2 = st.columns(2)
    with col1:
        num1 = st.text_input("Enter first number:", value="0")
    with col2:
        num2 = st.text_input("Enter second number:", value="0")

    operations = [
        "Add",
        "Subtract",
        "Multiply",
        "Divide",
        "Power",
        "Square Root (num1)",
        "Sin (num1)",
        "Cos (num1)",
        "Tan (num1)",
        "Log (num1)",
        "Factorial (num1)",
    ]
    operation = st.selectbox("Select operation:", operations)

    return num1, num2, operation


# Function to create a button layout
def create_button_layout():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_button = st.button("Calculate")
    return calculate_button
