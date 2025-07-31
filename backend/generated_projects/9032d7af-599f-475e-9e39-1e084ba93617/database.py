"""
Database configuration and initialization module.
This module creates the SQLAlchemy instance to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy

# Create the database instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
