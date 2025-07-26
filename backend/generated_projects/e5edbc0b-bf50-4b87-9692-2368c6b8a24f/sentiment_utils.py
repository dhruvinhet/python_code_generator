import nltk
from textblob import TextBlob
import re
import ssl
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure NLTK resources are downloaded
def download_nltk_resources():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        logging.info("Downloading wordnet...")
        nltk.download('wordnet')

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        logging.info("Downloading punkt...")
        nltk.download('punkt')

    try:
        nltk.data.find('sentiment/vader_lexicon')
    except LookupError:
        logging.info("Downloading vader_lexicon...")
        nltk.download('vader_lexicon')


try:
    download_nltk_resources()
except Exception as e:
    logging.error(f"Error downloading NLTK resources: {e}")


def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    text = text.strip()
    return text


def analyze_sentiment_textblob(text):
    try:
        processed_text = preprocess_text(text)
        analysis = TextBlob(processed_text)
        sentiment_score = analysis.sentiment.polarity
        return sentiment_score
    except Exception as e:
        logging.error(f"Error analyzing sentiment: {e}")
        return 0.0