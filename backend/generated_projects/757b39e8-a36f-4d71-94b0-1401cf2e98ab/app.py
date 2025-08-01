import logging
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS

from database import db, init_db # Import db and init_db
from models import User, Vehicle, Booking # Import models so SQLAlchemy knows them
from routes import api

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_app():
    app = Flask(__name__, 
                template_folder='templates', 
                static_folder='static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_very_secret_key_for_dev')
    
    # Use absolute path for database to avoid path issues
    db_dir = os.path.join(app.root_path, 'instance')
    db_path = os.path.join(db_dir, 'users.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    # Models are imported above, so db.create_all() will find them.
    init_db(app) 

    # Enable CORS for all origins, you might want to restrict this in production
    CORS(app)

    # Register blueprints
    app.register_blueprint(api)

    # Frontend serving routes for the multi-page application
    @app.route('/')
    def home_page():
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        return render_template('register.html')

    @app.route('/about')
    def about_page():
        return render_template('about.html')

    @app.route('/contact')
    def contact_page():
        return render_template('contact.html')

    @app.route('/favicon.ico')
    def favicon():
        # Ensure favicon is served correctly from static folder
        return app.send_static_file('favicon.ico')

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'404 Not Found: {request.path}')
        return jsonify({"message": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback() # Rollback in case of database errors
        app.logger.exception(f'500 Internal Server Error: {error}')
        return jsonify({"message": "Internal server error"}), 500

    app.logger.info('Flask application created and configured.')
    return app
