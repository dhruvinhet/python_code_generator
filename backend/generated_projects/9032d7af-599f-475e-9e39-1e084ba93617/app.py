from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os
from database import db, init_db

# Initialize Flask application with template and static folders
app = Flask(__name__, 
            template_folder='.',  # Look for templates in current directory
            static_folder='static')  # Static files in static folder

# Configure the database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'vehicle_rental.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking for performance
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key') # Set a secret key for session management, use environment variable for production

# Initialize database
init_db(app)

# Enable CORS for all routes
CORS(app)

# Import models to create them
from models import User, Vehicle, Booking

# Import and register routes after db is initialized
from routes import api
app.register_blueprint(api)

# Frontend routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Basic API route for testing
@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'Backend API is running'}

@app.route('/test')
def test_backend():
    return 'Hello, World! The backend is running.'

# Run the application if this script is executed
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
