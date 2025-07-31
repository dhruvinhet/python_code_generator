from flask import Blueprint, jsonify, request, abort
from database import db
from models import User, Vehicle, Booking
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
import logging

api = Blueprint('api', __name__, url_prefix='/api')

CORS(api)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'}), 200


@api.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    if request.method == 'GET':
        vehicles = Vehicle.query.all()
        return jsonify([{'id': v.id, 'make': v.make, 'model': v.model, 'year': v.year, 'type': v.type, 'availability': v.availability, 'image_url': v.image_url, 'description': v.description, 'price_per_day': v.price_per_day} for v in vehicles]), 200

    elif request.method == 'POST':
        data = request.get_json()
        try:
            new_vehicle = Vehicle(
                make=data['make'],
                model=data['model'],
                year=data['year'],
                type=data['type'],
                availability=data['availability'],
                image_url=data.get('image_url', ''),
                description=data.get('description', ''),
                price_per_day=data['price_per_day']
            )
            db.session.add(new_vehicle)
            db.session.commit()
            return jsonify({'message': 'Vehicle created successfully', 'id': new_vehicle.id}), 201
        except KeyError as e:
            logger.error(f"Missing key: {e}")
            abort(400, description=f"Missing key: {e}")
        except Exception as e:
            logger.exception("Error creating vehicle")
            db.session.rollback()
            abort(500, description=str(e))


@api.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify({
        'id': vehicle.id,
        'make': vehicle.make,
        'model': vehicle.model,
        'year': vehicle.year,
        'type': vehicle.type,
        'availability': vehicle.availability,
        'image_url': vehicle.image_url,
        'description': vehicle.description,
        'price_per_day': vehicle.price_per_day
    }), 200

@api.route('/bookings', methods=['POST', 'GET'])
def bookings():
    if request.method == 'POST':
        data = request.get_json()
        try:
            new_booking = Booking(
                vehicle_id=data['vehicle_id'],
                user_id=data['user_id'],
                start_date=data['start_date'],
                end_date=data['end_date']
            )
            db.session.add(new_booking)
            db.session.commit()
            return jsonify({'message': 'Booking created successfully', 'id': new_booking.id}), 201
        except KeyError as e:
            logger.error(f"Missing key: {e}")
            abort(400, description=f"Missing key: {e}")
        except Exception as e:
            logger.exception("Error creating booking")
            db.session.rollback()
            abort(500, description=str(e))

    elif request.method == 'GET':
        bookings = Booking.query.all()
        return jsonify([{'id': b.id, 'vehicle_id': b.vehicle_id, 'user_id': b.user_id, 'start_date': b.start_date, 'end_date': b.end_date} for b in bookings]), 200

@api.route('/users/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        username = data['username']
        password = data['password']  # In a real app, hash the password
        email = data['email']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
             return jsonify({'message': 'Username already exists'}), 400

        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except KeyError as e:
        logger.error(f"Missing key: {e}")
        abort(400, description=f"Missing key: {e}")
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error: {e}")
        abort(400, description="Username or email already exists.")
    except Exception as e:
        db.session.rollback()
        logger.exception("Error registering user")
        abort(500, description=str(e))


@api.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        username = data['username']
        password = data['password']  # In a real app, compare hashed passwords

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except KeyError as e:
        logger.error(f"Missing key: {e}")
        abort(400, description=f"Missing key: {e}")
    except Exception as e:
        logger.exception("Error logging in")
        abort(500, description=str(e))

@api.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': error.description}), 400

@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': 'Resource not found'}), 404

@api.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500
