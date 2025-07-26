# calculator.py

# A basic calculator application that performs addition, subtraction, multiplication, and division operations.


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
        y: The second number.

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
        x: The first number.
        y: The second number.

    Returns:
        The quotient of x and y. Returns an error message if dividing by zero.
    """
    if y == 0:
        return "Error: Cannot divide by zero."
    try:
        return x / y
    except TypeError:
        return "Error: Invalid input type."


def get_user_input():
    """Gets the operation and numbers from the user via command line input.

    Returns:
        A tuple containing the operation and the two numbers, or None if input is invalid.
    """
    try:
        operation = input("Enter operation (+, -, *, /): ")
        if operation not in ['+', '-', '*', '/']:
            print("Invalid operation. Please enter +, -, *, or /.")
            return None
        x = float(input("Enter first number: "))
        y = float(input("Enter second number: "))
        return operation, x, y
    except ValueError:
        print("Invalid input. Please enter numbers.")
        return None
    except EOFError:
        print("End of input.")
        return None


def perform_calculation(operation, x, y):
    """Performs the calculation based on the given operation and numbers.

    Args:
        operation: The operation to perform (+, -, *, /).
        x: The first number.
        y: The second number.

    Returns:
        The result of the calculation, or an error message if the operation is invalid.
    """
    try:
        if operation == '+':
            return add(x, y)
        elif operation == '-':
            return subtract(x, y)
        elif operation == '*':
            return multiply(x, y)
        elif operation == '/':
            return divide(x, y)
        else:
            return "Error: Invalid operation."
    except TypeError as e:
        return f"Error: Invalid input type: {e}"


def main():
    """The main function that orchestrates the calculator program.
    It gets user input, performs the calculation, and prints the result.
    """
    while True:
        user_input = get_user_input()
        if user_input is None:
            break  # Exit the loop if get_user_input returns None

        operation, x, y = user_input
        result = perform_calculation(operation, x, y)
        print("Result:", result)

        another_calculation = input("Do you want to perform another calculation? (yes/no): ").lower()
        if another_calculation != 'yes':
            break


if __name__ == "__main__":
    main()