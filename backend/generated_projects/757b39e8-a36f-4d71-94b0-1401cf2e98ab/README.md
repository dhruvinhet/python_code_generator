A modern, attractive login page featuring a glassmorphism design and a dynamic live background.

# GlassEffectLogin: A Modern Flask Web Application with Glassmorphism UI

This project integrates a Flask backend with a responsive Vanilla JavaScript frontend to create a modern web application featuring a stunning glassmorphism design and dynamic live backgrounds. It includes user authentication (login, registration) and showcases best practices for full-stack integration, error handling, and deployment configuration.

## Features

-   **User Login & Registration:** Secure user authentication with username/password.
-   **Glassmorphism UI Design:** Modern, frosted glass effect elements for a sleek look.
-   **Dynamic Live Background:** Engaging background video/animation for an immersive experience (primarily on Login/Register pages).
-   **Client-side Form Validation:** Real-time feedback for user input.
-   **Server-side User Authentication & Registration:** Robust backend logic for user management.
-   **Responsive Design:** Adapts seamlessly to various screen sizes (desktop, tablet, mobile).
-   **API Integration:** Clear separation and communication between frontend and backend via RESTful APIs.
-   **Comprehensive Error Handling:** User-friendly error messages and robust API error management.
-   **Sample Data:** Easily populate the database with test users and other entities for quick development.

## Project Structure

```
GlassEffectLogin/
├── instance/                 # Contains the SQLite database file (users.db)
├── static/
│   ├── css/                  # Frontend CSS files
│   │   └── style.css
│   ├── js/                   # Frontend JavaScript files
│   │   └── script.js
│   └── videos/               # Placeholder for background video (e.g., background.mp4)
├── templates/                # Jinja2 HTML templates served by Flask
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── about.html
│   └── contact.html
├── .env.example              # Template for environment variables
├── app.py                    # Flask application entry point, app creation, routes, error handlers
├── database.py               # SQLAlchemy database initialization (db object)
├── models.py                 # SQLAlchemy ORM models (User, Vehicle, Booking)
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── routes.py                 # API blueprint with login, register, and other API endpoints
├── run.py                    # Script to run the Flask development server
└── sample_data.py            # Script to populate the database with initial data
```

## Setup Instructions

Follow these steps to get the application up and running on your local machine.

### Prerequisites

*   Python 3.8+
*   pip (Python package installer)

### 1. Clone the Repository

```bash
git clone <repository-url> # Replace with your actual repository URL
cd GlassEffectLogin
```

### 2. Create a Python Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

*   **On Windows:**
    ```bash
    .\venv\Scripts\activate
    ```
*   **On macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

### 4. Install Dependencies

Install all required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory of the project based on `.env.example`.

```bash
cp .env.example .env
```

Open `.env` and replace `'a_strong_random_secret_key_here'` with a long, random string. This `SECRET_KEY` is crucial for security, especially for session management.

```ini
# .env
SECRET_KEY='your_super_secret_flask_key_here'
# Optional:
# FLASK_APP=run.py
# FLASK_ENV=development
```
*Note: For production, consider using a proper environment variable manager or a deployment service to set `SECRET_KEY` securely.*

### 6. Initialize and Populate the Database

The application uses SQLite, and the database file `users.db` will be created inside the `instance/` directory.

Run the `sample_data.py` script to create the database tables and populate them with some initial data (including a test user).

```bash
python sample_data.py
```
This will create `instance/users.db` and add default users like `admin:password` and `testuser:testpass`.

### 7. Run the Application

Start the Flask development server:

```bash
python run.py
```

The application should now be running at `http://localhost:8080`.

## Usage

*   Open your web browser and navigate to `http://localhost:8080`. You will be redirected to the login page.
*   **Login:** Use the sample credentials:
    *   **Username:** `admin`
    *   **Password:** `password`
    *   Or:
    *   **Username:** `testuser`
    *   **Password:** `testpass`
*   **Register:** Click "Register Here" on the login page to create a new account.
*   **Test API Connection:** On the login page, use the "Test API Connection" button to verify frontend-backend communication.
*   Explore other pages like Home, About, and Contact through the navigation bar. The Contact page form submission is handled client-side with a mock backend endpoint.

## Important Notes

*   **CORS:** Cross-Origin Resource Sharing (`Flask-Cors`) is enabled for all origins (`CORS(app)`) in `app.py` for development convenience. **In a production environment, you should restrict this to your specific frontend domain(s) for security reasons.**
    ```python
    # Example for production (in app.py):
    # CORS(app, origins=["https://yourfrontenddomain.com"])
    ```
*   **Dynamic Background:** The `static/videos/background.mp4` file is a placeholder. You will need to add your own video file to this path for the dynamic background to work. If the video fails to load, a CSS gradient animation is used as a fallback.
*   **Error Handling:** Both frontend and backend include comprehensive error handling. Frontend provides user-friendly messages and fallbacks for API unavailability. Backend logs errors and returns appropriate HTTP status codes.

Enjoy exploring the GlassEffectLogin application!
