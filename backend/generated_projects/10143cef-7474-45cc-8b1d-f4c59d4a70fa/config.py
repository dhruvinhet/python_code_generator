# config.py

"""
Configuration file for the Email Spam Classifier project.
Stores paths for datasets, trained models, and other configurable parameters.
"""

import os

# Base directory for the project (current directory of config.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
SPAM_DATASET_PATH = os.path.join(DATA_DIR, 'spam.csv') # Assuming a CSV file named spam.csv

# Model Paths
MODELS_DIR = os.path.join(BASE_DIR, 'models')
TRAINED_MODEL_PATH = os.path.join(MODELS_DIR, 'spam_classifier_model.joblib')
# Note: The TfidfVectorizer is part of the Pipeline, so it's saved with the model.

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Model Hyperparameters (if any, example)
# Can be expanded for more complex models or tuning
MODEL_PARAMS = {
    'tfidf__max_features': 5000,
    'tfidf__ngram_range': (1, 2),
    'mnb__alpha': 0.75, # Laplace smoothing parameter for Naive Bayes
}
