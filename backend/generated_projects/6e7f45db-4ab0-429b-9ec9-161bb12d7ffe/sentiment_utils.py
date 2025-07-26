# sentiment_utils.py
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def initialize_sentiment_analyzer():
    """Initializes the VADER sentiment analyzer."""
    return SentimentIntensityAnalyzer()


def get_sentiment_score(text, analyzer):
    """Computes the VADER sentiment score for a given text.

    Args:
        text (str): The text to analyze.
        analyzer (SentimentIntensityAnalyzer): The initialized sentiment analyzer.

    Returns:
        dict: A dictionary containing the sentiment scores (positive, negative, neutral, compound).
    """
    try:
        scores = analyzer.polarity_scores(text)
        return scores
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return {'pos': 0.0, 'neg': 0.0, 'neu': 0.0, 'compound': 0.0}