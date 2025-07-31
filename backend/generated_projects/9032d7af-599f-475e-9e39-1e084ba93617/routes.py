from flask import Blueprint, request, jsonify
from database import db
from models import User, Vehicle, Booking
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# Helper function to serialize SQLAlchemy objects to JSON
def serialize(obj):
    if isinstance(obj, Vehicle):
        return {
            'id': obj.id,
            'make': obj.make,
            'model': obj.model,
            'year': obj.year,
            'rental_price': obj.rental_price,
            'availability': obj.availability,
            'image_url': obj.image_url,
            'description': obj.description
        }
    elif isinstance(obj, User):
        return {
            'id': obj.id,
            'username': obj.username,
            'email': obj.email
        }
    elif isinstance(obj, Booking):
        return {
            'id': obj.id,
            'user_id': obj.user_id,
            'vehicle_id': obj.vehicle_id,
            'start_date': obj.start_date.isoformat(),
            'end_date': obj.end_date.isoformat(),
            'total_cost': obj.total_cost
        }
    else:
        return None

# API endpoint to retrieve all vehicles
@api.route('/vehicles', methods=['GET'])
def get_vehicles():
    try:
        vehicles = Vehicle.query.all()
        return jsonify([serialize(v) for v in vehicles])
    except Exception as e:
        logging.error(f"Error retrieving vehicles: {e}")
        return jsonify({'message': 'Error retrieving vehicles'}), 500

# API endpoint to retrieve a specific vehicle by ID
@api.route('/vehicles/<int:id>', methods=['GET'])
def get_vehicle(id):
    try:
        vehicle = Vehicle.query.get_or_404(id)
        return jsonify(serialize(vehicle))
    except Exception as e:
        logging.error(f"Error retrieving vehicle with id {id}: {e}")
        return jsonify({'message': 'Vehicle not found'}), 404

# API endpoint to create a new booking
@api.route('/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        vehicle_id = data.get('vehicle_id')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        if not all([user_id, vehicle_id, start_date_str, end_date_str]):
            return jsonify({'message': 'Missing required fields'}), 400

        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)

        # Calculate total cost (example calculation, adjust as needed)
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({'message': 'Vehicle not found'}), 404

        rental_days = (end_date - start_date).days
        total_cost = vehicle.rental_price * rental_days

        new_booking = Booking(user_id=user_id, vehicle_id=vehicle_id, start_date=start_date, end_date=end_date, total_cost=total_cost)

        db.session.add(new_booking)
        db.session.commit()
        return jsonify({'message': 'Booking created successfully', 'booking_id': new_booking.id}), 201

    except ValueError as ve:
        logging.error(f"Invalid date format: {ve}")
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DDTHH:MM:SS'}), 400
    except Exception as e:
        logging.error(f"Error creating booking: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error creating booking'}), 500

# API endpoint for user registration
@api.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({'message': 'Missing required fields'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already exists'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already exists'}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        logging.error(f"Error registering user: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error registering user'}), 500

# API endpoint for user login
@api.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Missing username or password'}), 400

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            return jsonify({'message': 'Login successful', 'user_id': user.id, 'username': user.username}), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401

    except Exception as e:
        logging.error(f"Error logging in user: {e}")
        return jsonify({'message': 'Error logging in'}), 500
