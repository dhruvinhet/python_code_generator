from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os

from database import db, init_db
from models import User, Vehicle, Booking # Import models for database initialization.
from routes import api


def create_app():
    app = Flask(__name__, template_folder='.', static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./vehicle_rental.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key' # Change in production
    CORS(app)

    init_db(app)
    app.register_blueprint(api)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/static/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path)
    
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/test')
    def test():
        return 'Backend is working!'

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080)
