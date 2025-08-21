# model_trainer.py

"""
Manages the training pipeline including feature extraction (TF-IDF),
model selection (e.g., Naive Bayes), model training, and persistence.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os
import pandas as pd # For type hinting and input DataFrame
from config import TRAINED_MODEL_PATH, MODEL_PARAMS

def train_model(data: pd.DataFrame) -> Pipeline:
    """
    Trains a machine learning model pipeline for spam classification.
    The pipeline includes TF-IDF vectorization and a Multinomial Naive Bayes classifier.

    Args:
        data (pd.DataFrame): The input DataFrame containing 'text' and 'label' columns.

    Returns:
        sklearn.pipeline.Pipeline: The trained machine learning pipeline.
                                   Returns None if training fails.
    """
    if data.empty or 'text' not in data.columns or 'label' not in data.columns:
        print("Error: Input data is empty or missing 'text'/'label' columns for training.")
        return None

    X = data['text']
    y = data['label']

    print("Starting model training...")

    try:
        # Create a pipeline with TF-IDF vectorizer and Multinomial Naive Bayes classifier
        # The parameters for TF-IDF and MNB can be configured via MODEL_PARAMS
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=MODEL_PARAMS.get('tfidf__max_features', 5000),
                ngram_range=MODEL_PARAMS.get('tfidf__ngram_range', (1, 1))
            )),
            ('mnb', MultinomialNB(
                alpha=MODEL_PARAMS.get('mnb__alpha', 1.0) # Default alpha for Naive Bayes
            ))
        ])

        # Train the model
        pipeline.fit(X, y)
        print("Model training completed successfully.")
        return pipeline
    except Exception as e:
        print(f"An error occurred during model training: {e}")
        return None

def save_model(model: Pipeline, path: str = TRAINED_MODEL_PATH):
    """
    Saves the trained machine learning pipeline to a specified file path using joblib.

    Args:
        model (sklearn.pipeline.Pipeline): The trained scikit-learn pipeline to save.
        path (str): The file path where the model should be saved.
    """
    if model is None:
        print("Error: No model provided to save.")
        return

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(model, path)
        print(f"Model saved successfully to {path}")
    except Exception as e:
        print(f"An error occurred while saving the model: {e}")
