# calculator.py

# This module contains the core calculator logic and arithmetic functions.


def add(x, y):
    """Adds two numbers.

    Args:
        x: The first number.
        y: The second number.

    Returns:
        The sum of x and y.
    """
    return x + y


def subtract(x, y):
    """Subtracts one number from another.

    Args:
        x: The first number.
        y: The second number to subtract from x.

    Returns:
        The difference between x and y.
    """
    return x - y


def multiply(x, y):
    """Multiplies two numbers.

    Args:
        x: The first number.
        y: The second number.

    Returns:
        The product of x and y.
    """
    return x * y


def divide(x, y):
    """Divides one number by another.

    Args:
        x: The dividend.
        y: The divisor.

    Returns:
        The quotient of x and y.

    Raises:
        ZeroDivisionError: If y is zero.
    """
    if y == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return x / y


def calculate(operation, x, y):
    """Performs a calculation based on the specified operation.

    Args:
        operation: A string representing the operation to perform ('add', 'subtract', 'multiply', 'divide').
        x: The first number.
        y: The second number.

    Returns:
        The result of the calculation.

    Raises:
        ValueError: If the operation is invalid.
        ZeroDivisionError: If attempting to divide by zero.
    """
    try:
        if operation == 'add':
            return add(x, y)
        elif operation == 'subtract':
            return subtract(x, y)
        elif operation == 'multiply':
            return multiply(x, y)
        elif operation == 'divide':
            return divide(x, y)
        else:
            raise ValueError("Invalid operation: {}".format(operation))
    except ZeroDivisionError as e:
        raise e
    except ValueError as e:
        raise e
