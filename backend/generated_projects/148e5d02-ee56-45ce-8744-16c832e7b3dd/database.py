from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()

        # Optional: Seed data for initial setup
        # from models import User, Vehicle
        # if not User.query.first():  # Check if database is empty
        #     user = User(username='admin', password='password', email='admin@example.com') # Remember to hash passwords in real app
        #     db.session.add(user)
        #     db.session.commit()
        #     print("Sample data added to the database.")

        print("Database initialized.")
