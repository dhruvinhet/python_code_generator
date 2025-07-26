# Scientific Calculator

A powerful scientific calculator built with Python and Streamlit, featuring a user-friendly web interface for performing various mathematical operations.

## Features

- **Basic Operations**: Addition, Subtraction, Multiplication, Division
- **Advanced Functions**: Power, Square Root, Logarithms (base 10 and natural)
- **Trigonometric Functions**: Sine, Cosine, Tangent
- **Unit Conversions**: Degrees to Radians and vice versa
- **Special Functions**: Factorial, Exponential
- **Interactive Web Interface**: Clean and intuitive Streamlit-based GUI

## Installation Requirements

### Required Python Packages
```bash
pip install streamlit
```

### Python Version
- Python 3.7 or higher

## How to Run the Application

### Method 1: Using the Main Entry Point (Recommended)
```bash
python main.py
```
This will automatically:
- Detect that it's a Streamlit application
- Install Streamlit if not already installed
- Launch the application on http://localhost:8501

### Method 2: Direct Streamlit Command
```bash
streamlit run src/user_interface.py
```

### Method 3: Using the Streamlit Module
```bash
python -m streamlit run src/user_interface.py
```

## Usage Instructions

1. **Start the Application**: Run `python main.py`
2. **Open Browser**: Navigate to http://localhost:8501 (opens automatically)
3. **Select Operation**: Use the sidebar dropdown to choose your desired mathematical operation
4. **Enter Numbers**: Input the required numbers in the provided fields
5. **View Results**: The result will be displayed immediately on the main interface

## Project Structure

```
scientific-calculator/
├── main.py                    # Main entry point - handles different execution contexts
├── src/
│   ├── calculator_logic.py    # Core mathematical functions and calculations
│   └── user_interface.py      # Streamlit web interface and user interactions
├── requirements.txt           # Python package dependencies
└── README.md                 # This documentation file
```

### File Descriptions

- **main.py**: Universal entry point that detects the application type and runs it appropriately
- **src/calculator_logic.py**: Contains all mathematical functions (add, subtract, multiply, etc.)
- **src/user_interface.py**: Streamlit application with the web interface
- **requirements.txt**: Lists all required Python packages

## Available Operations

### Basic Arithmetic
- **Addition**: Add two numbers
- **Subtraction**: Subtract second number from first
- **Multiplication**: Multiply two numbers
- **Division**: Divide first number by second (with zero-division protection)

### Scientific Functions
- **Power**: Raise first number to the power of second number
- **Square Root**: Calculate square root of the input number
- **Logarithm (base 10)**: Calculate log₁₀ of the input
- **Natural Logarithm**: Calculate ln of the input
- **Exponential**: Calculate e^x of the input

### Trigonometric Functions
- **Sine**: Calculate sin(x) where x is in radians
- **Cosine**: Calculate cos(x) where x is in radians  
- **Tangent**: Calculate tan(x) where x is in radians

### Utility Functions
- **Factorial**: Calculate n! of the input number
- **Degrees to Radians**: Convert degrees to radians
- **Radians to Degrees**: Convert radians to degrees

## Configuration Options

The application runs with default Streamlit settings:
- **Port**: 8501
- **Host**: localhost
- **Auto-reload**: Enabled during development

To customize these settings, you can modify the Streamlit configuration or pass parameters to the streamlit run command.

## Troubleshooting

### Common Issues

1. **"Streamlit not found" Error**
   - Solution: Install Streamlit with `pip install streamlit`
   - Or run `python main.py` which will auto-install it

2. **Port Already in Use**
   - Solution: Use a different port: `streamlit run src/user_interface.py --server.port 8502`

3. **Import Errors**
   - Ensure you're running from the project root directory
   - Check that all files are in their correct locations

4. **Browser Doesn't Open Automatically**
   - Manually navigate to http://localhost:8501
   - Check firewall settings if accessing from another device

### Running in Different Environments

**Development**: Use `python main.py` for auto-detection and setup
**Production**: Use `streamlit run src/user_interface.py` with appropriate server settings
**Docker**: Expose port 8501 and use `--server.headless true`

## Technical Details for Developers

### Architecture Overview
- **Frontend**: Streamlit web interface
- **Backend**: Pure Python mathematical functions
- **Entry Point**: Adaptive main.py that handles different execution contexts

### Code Organization
- Separation of concerns: UI logic separate from business logic
- Modular design: Each mathematical operation is a separate function
- Error handling: Division by zero and invalid input protection
- Type hints: Functions include proper type annotations

### Testing the Application
```bash
# Test core functionality
python -c "from src.calculator_logic import add; print(add(2, 3))"

# Test UI components (requires Streamlit)
python main.py
```

## Future Enhancement Possibilities

1. **Scientific Constants**: Add π, e, c (speed of light), etc.
2. **Memory Functions**: Store and recall previous calculations
3. **History**: Keep track of calculation history
4. **Graph Plotting**: Visualize functions and equations
5. **Unit Conversions**: Length, weight, temperature conversions
6. **Complex Numbers**: Support for complex number operations
7. **Matrix Operations**: Basic linear algebra functions
8. **Export Features**: Save calculations to PDF or CSV
9. **Themes**: Dark/light mode toggle
10. **Mobile Optimization**: Responsive design for mobile devices

## Developer Notes

The application is designed to be easily extensible. To add new mathematical operations:

1. Add the function to `src/calculator_logic.py`
2. Update the operation list in `src/user_interface.py`
3. Add the corresponding condition in the calculation logic

The main.py file automatically handles different application types and can be used as a template for other Python projects.

---

**Version**: 1.0  
**Python Version**: 3.7+  
**Framework**: Streamlit  
**License**: Open Source
