from flask import Blueprint, request, jsonify, current_app
from database import db
from models import User, Vehicle, Booking # Ensure User is imported for registration
from datetime import datetime
from werkzeug.security import generate_password_hash # Import for registration

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/status', methods=['GET'])
def health_check():
    """Endpoint for API health/status check."""
    current_app.logger.info('API status check requested.')
    return jsonify({"status": "ok", "message": "Backend API is healthy!"}), 200

@api.route('/login', methods=['POST'])
def login():
    """Authenticates a user based on username and password."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        current_app.logger.warning('Login attempt with missing credentials.')
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        current_app.logger.info(f'User {username} logged in successfully.')
        # In a real app, you would generate a session token or JWT here.
        return jsonify({"message": "Login successful", "user_id": user.id, "username": user.username}), 200
    else:
        current_app.logger.warning(f'Failed login attempt for user {username}.')
        return jsonify({"message": "Invalid username or password"}), 401

@api.route('/register', methods=['POST'])
def register():
    """Registers a new user."""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email') # Assuming email for registration, though not in User model
    password = data.get('password')

    if not all([username, password]): # Email is not in User model, so only check username/password
        return jsonify({"message": "Username and password are required for registration."}), 400
    
    # Basic validation (more robust validation should be done client-side AND server-side)
    if len(username) < 3 or len(password) < 6:
        return jsonify({"message": "Username must be at least 3 characters and password at least 6."}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        current_app.logger.warning(f'Registration attempt with existing username: {username}.')
        return jsonify({"message": "Username already exists. Please choose a different one."}), 409 # Conflict

    try:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        current_app.logger.info(f'New user registered: {username}.')
        return jsonify({"message": "Registration successful!", "user_id": new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error during user registration: {e}')
        return jsonify({"message": "An error occurred during registration. Please try again."}), 500

@api.route('/contact', methods=['POST'])
def contact():
    """Mock endpoint for contact form submission."""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not all([name, email, message]):
        return jsonify({"message": "All contact form fields are required."}), 400
    
    current_app.logger.info(f'Contact form submission received from {name} ({email}): {message[:50]}...')
    # In a real app, you would save this to a database, send an email, etc.
    return jsonify({"message": "Your message has been received successfully. We will get back to you soon!"}), 200

# Vehicle and Booking routes from original backend code
@api.route('/vehicles', methods=['GET'])
def get_vehicles():
    try:
        vehicles = Vehicle.query.all()
        return jsonify([v.to_dict() for v in vehicles]), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving vehicles: {e}')
        return jsonify({"message": "Internal server error"}), 500

@api.route('/vehicles', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    make = data.get('make')
    model = data.get('model')
    year = data.get('year')
    daily_rate = data.get('daily_rate')

    if not all([make, model, year, daily_rate]):
        return jsonify({"message": "Make, model, year, and daily_rate are required"}), 400
    if not isinstance(year, int) or year <= 1900 or year > datetime.now().year + 5:
        return jsonify({"message": "Invalid year"}), 400
    if not isinstance(daily_rate, (int, float)) or daily_rate <= 0:
        return jsonify({"message": "Daily rate must be a positive number"}), 400

    try:
        new_vehicle = Vehicle(make=make, model=model, year=year, daily_rate=daily_rate)
        db.session.add(new_vehicle)
        db.session.commit()
        current_app.logger.info(f'New vehicle added: {new_vehicle.make} {new_vehicle.model}')
        return jsonify(new_vehicle.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error adding vehicle: {e}')
        return jsonify({"message": "Internal server error"}), 500

@api.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if vehicle:
            return jsonify(vehicle.to_dict()), 200
        else:
            return jsonify({"message": "Vehicle not found"}), 404
    except Exception as e:
        current_app.logger.error(f'Error retrieving vehicle {vehicle_id}: {e}')
        return jsonify({"message": "Internal server error"}), 500

@api.route('/bookings', methods=['GET'])
def get_bookings():
    try:
        bookings = Booking.query.all()
        return jsonify([b.to_dict() for b in bookings]), 200
    except Exception as e:
        current_app.logger.error(f'Error retrieving bookings: {e}')
        return jsonify({"message": "Internal server error"}), 500

@api.route('/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    user_id = data.get('user_id')
    vehicle_id = data.get('vehicle_id')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not all([user_id, vehicle_id, start_date_str, end_date_str]):
        return jsonify({"message": "User ID, Vehicle ID, Start Date, and End Date are required"}), 400

    try:
        user = User.query.get(user_id)
        vehicle = Vehicle.query.get(vehicle_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        if not vehicle:
            return jsonify({"message": "Vehicle not found"}), 404

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if start_date >= end_date:
            return jsonify({"message": "Start date must be before end date"}), 400
        if start_date < datetime.now().date():
            return jsonify({"message": "Start date cannot be in the past"}), 400

        duration_days = (end_date - start_date).days
        total_cost = duration_days * vehicle.daily_rate

        new_booking = Booking(user_id=user_id, vehicle_id=vehicle_id, 
                              start_date=start_date_str, end_date=end_date_str, 
                              total_cost=total_cost)
        db.session.add(new_booking)
        db.session.commit()
        current_app.logger.info(f'New booking created for user {user_id} and vehicle {vehicle_id}.')
        return jsonify(new_booking.to_dict()), 201

    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating booking: {e}')
        return jsonify({"message": "Internal server error"}), 500
