# AVL Tree Visualizer

A web application that allows users to input numbers and visualize the creation of an AVL Tree.

## Features

*   Accept numeric input from the user.
*   Build AVL tree structure on the backend.
*   Visualize the AVL tree dynamically on the frontend.
*   Responsive user interface with an aesthetic design.

## Architecture

This application follows a client-server architecture:
*   **Frontend**: Built with vanilla HTML, CSS, and JavaScript. It handles user input, communicates with the backend via a RESTful API, and renders the AVL tree visualization.
*   **Backend**: A Flask application that contains the core AVL tree logic. It receives numbers from the frontend, constructs the AVL tree, and returns its structured representation (JSON) to the frontend for visualization.

## Setup and Run Instructions

Follow these steps to set up and run the application locally.

### Prerequisites

*   Python 3.8+
*   pip (Python package installer)

### 1. Clone the repository

```bash
git clone <repository_url> # Replace with your repository URL if applicable
cd AVLTreeVisualizer
```

### 2. Create and Activate a Virtual Environment (Recommended)

It's good practice to use a virtual environment to manage dependencies.

```bash
python -m venv venv
# On Windows
v_env\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory of the project based on the `.env.example` file.

```bash
cp .env.example .env
```

You can open `.env` and modify the `SECRET_KEY` if you wish, but for local development, the default is fine. Ensure `FLASK_RUN_PORT` is set to `8080`.

### 5. Run the Application

The application can be started using the `run.py` script.

```bash
python run.py
```

The Flask development server will start, typically on `http://127.0.0.1:8080` (or the port specified in `.env`).

### 6. Access the Application

Open your web browser and navigate to:

```
http://localhost:8080
```

You can now enter comma-separated numbers (e.g., `10, 5, 15, 3, 7, 12, 18`) into the input field and click "Build Tree" to visualize the AVL tree.

## Project Structure

```
.
├── app.py                  # Main Flask application entry point
├── avl_tree.py             # Core AVL Tree data structure and algorithms
├── routes.py               # Defines API endpoints, including /api/build-avl-tree
├── run.py                  # Script to run the Flask development server
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── README.md               # Project documentation
├── templates/
│   └── index.html          # Main HTML template for the UI
└── static/
    ├── css/
    │   └── style.css       # Styles for the web UI
    └── js/
        └── script.js       # Frontend interactivity (API calls, rendering)
```

## API Endpoints

*   **POST `/api/build-avl-tree`**
    *   **Purpose**: Receives a list of numbers, builds an AVL tree, and returns its structured representation.
    *   **Request Body (JSON)**:
        ```json
        {
            "numbers": [10, 5, 15, 3, 7]
        }
        ```
    *   **Response Body (JSON)**:
        ```json
        {
            "tree": {
                "value": 10,
                "height": 2,
                "left": { ... },
                "right": { ... }
            }
        }
        ```

## Contributing

Feel free to fork the repository and contribute.
