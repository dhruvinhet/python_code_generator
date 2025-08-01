from flask import Blueprint, request, jsonify
from flask_cors import CORS
import json
from database import db
from models import Question
import logging

logging.basicConfig(level=logging.DEBUG)

api = Blueprint('api', __name__, url_prefix='/api')
CORS(api)

@api.route('/health', methods=['GET'])
def health_check():
    logging.info("Health check requested")
    return jsonify({'status': 'OK'}), 200

@api.route('/questions', methods=['GET'])
def get_questions():
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')

    if not category or not difficulty:
        logging.error("Category or difficulty not provided")
        return jsonify({'error': 'Category and difficulty are required'}), 400

    questions = Question.query.filter_by(category=category, difficulty=difficulty).all()

    question_list = []
    for question in questions:
        question_list.append({
            'id': question.id,
            'category': question.category,
            'difficulty': question.difficulty,
            'text': question.text,
            'options': json.loads(question.options),  # Parse JSON options
            'correct_answer': question.correct_answer
        })

    logging.info(f"Retrieved {len(question_list)} questions")
    return jsonify(question_list), 200

@api.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    if not data or 'question_id' not in data or 'answer' not in data:
        logging.error("Invalid request data")
        return jsonify({'error': 'Question ID and answer are required'}), 400

    question_id = data['question_id']
    answer = data['answer']

    question = Question.query.get(question_id)

    if not question:
        logging.error(f"Question with ID {question_id} not found")
        return jsonify({'error': 'Question not found'}), 404

    is_correct = (answer == question.correct_answer)

    logging.info(f"Answer submitted for question {question_id}: {is_correct}")
    return jsonify({'correct': is_correct}), 200
