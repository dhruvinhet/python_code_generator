from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from transformers import pipeline

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    sentiment_pipeline = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
    model_loaded = True
except Exception as e:
    logger.error(f'Error loading model: {e}')
    sentiment_pipeline = None
    model_loaded = False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Sentiment Analysis Backend', 'model_loaded': model_loaded})

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text'}, 400)
        text = data['text']

        if sentiment_pipeline:
            try:
                result = sentiment_pipeline(text)[0]
                return jsonify({'result': result, 'status': 'success'})
            except Exception as e:
                logger.error(f'Error during inference: {e}')
                return jsonify({'result': {'label': 'neutral', 'score': 0.5}, 'status': 'fallback'})
        else:
            return jsonify({'result': {'label': 'neutral', 'score': 0.5}, 'status': 'model_unavailable'})
    except Exception as e:
        logger.error(f'Error: {e}')
        return jsonify({'error': str(e)}, 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)