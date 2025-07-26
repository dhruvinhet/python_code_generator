# src/calculator_logic.py

# This module contains the core calculation logic for the scientific calculator.

import math


def add(x, y):
    """Adds two numbers.

    Args:
        x (float): The first number.
        y (float): The second number.

    Returns:
        float: The sum of x and y.
    """
    return x + y


def subtract(x, y):
    """Subtracts two numbers.

    Args:
        x (float): The first number.
        y (float): The second number.

    Returns:
        float: The difference of x and y.
    """
    return x - y


def multiply(x, y):
    """Multiplies two numbers.

    Args:
        x (float): The first number.
        y (float): The second number.

    Returns:
        float: The product of x and y.
    """
    return x * y


def divide(x, y):
    """Divides two numbers.

    Args:
        x (float): The first number.
        y (float): The second number.

    Returns:
        float: The quotient of x and y.

    Raises:
        ZeroDivisionError: If y is zero.
    """
    if y == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return x / y


def power(x, y):
    """Calculates x raised to the power of y.

    Args:
        x (float): The base.
        y (float): The exponent.

    Returns:
        float: x raised to the power of y.
    """
    return x ** y


def square_root(x):
    """Calculates the square root of a number.

    Args:
        x (float): The number.

    Returns:
        float: The square root of x.

    Raises:
        ValueError: If x is negative.
    """
    if x < 0:
        raise ValueError("Cannot calculate square root of a negative number.")
    return math.sqrt(x)


def logarithm(x):
    """Calculates the base-10 logarithm of a number.

    Args:
        x (float): The number.

    Returns:
        float: The base-10 logarithm of x.

    Raises:
        ValueError: If x is not positive.
    """
    if x <= 0:
        raise ValueError("Cannot calculate logarithm of a non-positive number.")
    return math.log10(x)


def sine(x):
    """Calculates the sine of an angle (in radians).

    Args:
        x (float): The angle in radians.

    Returns:
        float: The sine of x.
    """
    return math.sin(x)


def cosine(x):
    """Calculates the cosine of an angle (in radians).

    Args:
        x (float): The angle in radians.

    Returns:
        float: The cosine of x.
    """
    return math.cos(x)


def tangent(x):
    """Calculates the tangent of an angle (in radians).

    Args:
        x (float): The angle in radians.

    Returns:
        float: The tangent of x.

    Raises:
        ValueError: If cosine(x) is close to zero.
    """
    if abs(math.cos(x)) < 1e-9:  # Check if cosine is close to zero
        raise ValueError("Tangent is undefined at this angle.")
    return math.tan(x)


def factorial(x):
    """Calculates the factorial of a non-negative integer.

    Args:
        x (int): The non-negative integer.

    Returns:
        int: The factorial of x.

    Raises:
        ValueError: If x is negative or not an integer.
    """
    if not isinstance(x, int) or x < 0:
        raise ValueError("Factorial is only defined for non-negative integers.")
    return math.factorial(x)


def degrees_to_radians(x):
    """Converts degrees to radians.

    Args:
        x (float): The angle in degrees.

    Returns:
        float: The angle in radians.
    """
    return math.radians(x)


def radians_to_degrees(x):
    """Converts radians to degrees.

    Args:
        x (float): The angle in radians.

    Returns:
        float: The angle in degrees.
    """
    return math.degrees(x)


def natural_logarithm(x):
    """Calculates the natural logarithm (base e) of a number.

    Args:
        x (float): The number.

    Returns:
        float: The natural logarithm of x.

    Raises:
        ValueError: If x is not positive.
    """
    if x <= 0:
        raise ValueError("Cannot calculate natural logarithm of a non-positive number.")
    return math.log(x)


def exponent(x):
    """Calculates e raised to the power of x.

    Args:
        x (float): The exponent.

    Returns:
        float: e raised to the power of x.
    """
    return math.exp(x)
