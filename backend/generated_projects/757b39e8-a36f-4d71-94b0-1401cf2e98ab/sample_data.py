import os
import click
from werkzeug.security import generate_password_hash
from app import create_app # Import create_app to get application context
from database import db
from models import User, Vehicle, Booking

def populate_sample_data():
    """Populates the database with sample data if tables are empty."""
    app = create_app()
    with app.app_context():
        # Ensure tables are created (idempotent)
        db.create_all()

        # Insert sample user data if tables are empty
        if User.query.count() == 0:
            click.echo('Adding sample user data...')
            # password 'password' hashed
            hashed_password = generate_password_hash('password', method='pbkdf2:sha256')
            admin_user = User(username='admin', password_hash=hashed_password)
            test_user = User(username='testuser', password_hash=generate_password_hash('testpass', method='pbkdf2:sha256'))
            db.session.add(admin_user)
            db.session.add(test_user)
            db.session.commit()
            click.echo('Sample users added.')
        else:
            click.echo('Users table already populated.')

        # Insert sample vehicle data if tables are empty
        if Vehicle.query.count() == 0:
            click.echo('Adding sample vehicle data...')
            vehicle1 = Vehicle(make='Toyota', model='Camry', year=2020, daily_rate=50.00)
            vehicle2 = Vehicle(make='Honda', model='Civic', year=2022, daily_rate=45.00)
            vehicle3 = Vehicle(make='Tesla', model='Model 3', year=2023, daily_rate=100.00)
            db.session.add_all([vehicle1, vehicle2, vehicle3])
            db.session.commit()
            click.echo('Sample vehicles added.')
        else:
            click.echo('Vehicles table already populated.')

        # Insert sample booking data if tables are empty and users/vehicles exist
        if Booking.query.count() == 0 and User.query.count() > 0 and Vehicle.query.count() > 0:
            click.echo('Adding sample booking data...')
            user_id = User.query.first().id
            vehicle_id = Vehicle.query.first().id
            if user_id and vehicle_id:
                booking1 = Booking(user_id=user_id, vehicle_id=vehicle_id, start_date='2023-10-26', end_date='2023-10-28', total_cost=100.00)
                db.session.add(booking1)
                db.session.commit()
                click.echo('Sample booking added.')
        else:
            click.echo('Bookings table already populated or no users/vehicles to link.')

        click.echo('Database initialization and sample data check complete.')

if __name__ == '__main__':
    populate_sample_data()
