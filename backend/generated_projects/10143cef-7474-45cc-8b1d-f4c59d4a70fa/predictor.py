# predictor.py

"""
Loads the trained model and vectorizer, then uses them to classify new,
unseen email texts as spam or not spam.
"""

import joblib
import os
from data_loader import preprocess_text # Import preprocessing function
from config import TRAINED_MODEL_PATH

def load_model(path: str = TRAINED_MODEL_PATH):
    """
    Loads a trained machine learning model pipeline from a specified file path.

    Args:
        path (str): The file path from which to load the model.

    Returns:
        sklearn.pipeline.Pipeline: The loaded scikit-learn pipeline.
                                   Returns None if loading fails or model file not found.
    """
    if not os.path.exists(path):
        print(f"Error: Model file not found at {path}. Please train the model first.")
        return None
    try:
        model = joblib.load(path)
        print(f"Model loaded successfully from {path}")
        return model
    except Exception as e:
        print(f"An error occurred while loading the model: {e}")
        return None

def classify_email(email_text: str, model) -> str:
    """
    Classifies a given email text as 'spam' or 'ham' (not spam) using the loaded model.

    Args:
        email_text (str): The raw text content of the email to classify.
        model: The trained scikit-learn pipeline (loaded via joblib).

    Returns:
        str: 'spam' if the email is classified as spam, 'ham' otherwise.
             Returns 'Error' if the model is not loaded or prediction fails.
    """
    if model is None:
        print("Error: Model is not loaded. Cannot classify email.")
        return "Error: Model not loaded"

    try:
        # Preprocess the email text using the same function used during training
        processed_text = preprocess_text(email_text)

        # Predict using the loaded model
        # The model expects an iterable, so we pass [processed_text]
        prediction = model.predict([processed_text])
        prediction_proba = model.predict_proba([processed_text])

        # prediction[0] will be 0 for ham, 1 for spam
        result = "spam" if prediction[0] == 1 else "ham"
        confidence = prediction_proba[0][prediction[0]] * 100 # Confidence for the predicted class

        print(f"Classification result: '{result}' with {confidence:.2f}% confidence.")
        return result
    except Exception as e:
        print(f"An error occurred during classification: {e}")
        return "Error during classification"
