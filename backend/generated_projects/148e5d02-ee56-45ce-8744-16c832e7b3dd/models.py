from database import db
from sqlalchemy.orm import relationship

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Store password hashes, not plain text
    email = db.Column(db.String(120), unique=True, nullable=False)
    bookings = relationship("Booking", back_populates="user")

    def __repr__(self):
        return f'<User {self.username}>'


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer)
    type = db.Column(db.String(50))
    availability = db.Column(db.Boolean, default=True)
    bookings = relationship("Booking", back_populates="vehicle")
    image_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    price_per_day = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Vehicle {self.make} {self.model}>'


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=False)
    vehicle = relationship("Vehicle", back_populates="bookings")
    user = relationship("User", back_populates="bookings")

    def __repr__(self):
        return f'<Booking {self.id}>'
