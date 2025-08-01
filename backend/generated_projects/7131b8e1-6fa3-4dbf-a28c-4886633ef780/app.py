from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import logging
import json
from database import db, init_db
from models import Question
from routes import api

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, template_folder='.', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gkquiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
init_db(app)
app.register_blueprint(api)


@app.route('/')
def index():
    logging.info("Serving index.html")
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    logging.info(f"Serving static file: {path}")
    return send_from_directory('static', path)

@app.route('/favicon.ico')
def favicon():
    logging.info("Serving favicon.ico")
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(404)
def not_found(error):
    logging.error(f"404 Error: {error}")
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    logging.error(f"500 Error: {error}")
    return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/test')
def test_route():
    logging.info("Test route accessed")
    return 'Backend is working!', 200


if __name__ == '__main__':
    with app.app_context():
        # Check if questions are already in the database
        if not Question.query.first():
            # Load sample questions from JSON file
            with open('questions.json', 'r') as f:
                questions_data = json.load(f)
            
            # Add sample questions to the database
            for q_data in questions_data:
                question = Question(
                    category=q_data['category'],
                    difficulty=q_data['difficulty'],
                    text=q_data['text'],
                    options=json.dumps(q_data['options']),
                    correct_answer=q_data['correct_answer']
                )
                db.session.add(question)
            db.session.commit()
            logging.info("Sample questions added to the database.")

    app.run(debug=True, port=8080)
