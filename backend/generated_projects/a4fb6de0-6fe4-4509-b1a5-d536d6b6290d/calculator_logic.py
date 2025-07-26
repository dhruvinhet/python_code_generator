# calculator_logic.py
import math
import numpy as np


# Function to add two numbers
def add(x, y):
    return x + y


# Function to subtract two numbers
def subtract(x, y):
    return x - y


# Function to multiply two numbers
def multiply(x, y):
    return x * y


# Function to divide two numbers
def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y


# Function to calculate the power of a number
def power(x, y):
    return x ** y


# Function to calculate the square root of a number
def square_root(x):
    return math.sqrt(x)


# Function to calculate the sine of a number (in radians)
def sin(x):
    return math.sin(x)


# Function to calculate the cosine of a number (in radians)
def cos(x):
    return math.cos(x)


# Function to calculate the tangent of a number (in radians)
def tan(x):
    return math.tan(x)


# Function to calculate the logarithm of a number (base e)
def log(x):
    return math.log(x)


# Function to calculate the factorial of a number
def factorial(x):
    return math.factorial(x)
