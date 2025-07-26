# main.py

# This is the entry point for the calculator application. It handles user
# input and output and calls the appropriate functions from calculator.py.

import calculator


def main():
    """Main function to run the calculator application."""
    operation_map = {
        '1': ('add', 'Addition'),
        '2': ('subtract', 'Subtraction'),
        '3': ('multiply', 'Multiplication'),
        '4': ('divide', 'Division')
    }

    while True:
        print("\nBasic Calculator")
        print("1. Add")
        print("2. Subtract")
        print("3. Multiply")
        print("4. Divide")
        print("5. Exit")

        choice = input("Enter choice(1/2/3/4/5): ")

        if choice == '5':
            print("Exiting calculator.")
            break

        if choice in operation_map:
            try:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))

                operation, operation_name = operation_map[choice]
                result = calculator.calculate(operation, num1, num2)

                print(f"{operation_name} Result: {result}")

            except ValueError:
                print("Invalid input. Please enter numbers only.")
            except ZeroDivisionError as e:
                print(e)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        else:
            print("Invalid input. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
