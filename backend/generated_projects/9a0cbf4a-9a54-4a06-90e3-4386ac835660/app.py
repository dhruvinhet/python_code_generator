from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
import logging
import os

# Import necessary modules for application factory pattern
from routes import api

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

def create_app():
    app = Flask(
        __name__,
        template_folder='templates', # Points to the 'templates' directory
        static_folder='static'     # Points to the 'static' directory
    )

    # Configuration
    # SECRET_KEY is essential for Flask's session management and other security features
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_key_change_this_in_production')

    # Enable CORS for all routes (important for frontend-backend communication on different ports/origins)
    CORS(app)
    app.logger.info("CORS enabled for the application.")

    # Register API blueprint
    app.register_blueprint(api)
    app.logger.info("API blueprint registered.")

    # Frontend Serving Routes
    @app.route('/')
    def index():
        app.logger.info("Serving index.html.")
        return render_template('index.html')

    @app.route('/favicon.ico')
    def favicon():
        app.logger.info("Serving favicon.ico.")
        # Assuming favicon.ico is in the static folder
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    # Global Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"404 Not Found: {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "API endpoint not found", "path": request.path}), 404
        # For a simple app, we can just render the index page or a custom 404 page.
        # For this project, we don't have a 404.html specified, so redirecting to home or simple JSON.
        return jsonify({"error": "Page not found", "path": request.path}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"500 Internal Server Error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    app.logger.info("Flask application created and configured.")
    return app
