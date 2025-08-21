# main.py

"""
Entry point of the Email Spam Classifier application.
Orchestrates data loading, model training, and provides a simple interface for email classification.
"""

import os
import nltk
from data_loader import load_dataset, preprocess_text
from model_trainer import train_model, save_model
from predictor import load_model, classify_email
from config import SPAM_DATASET_PATH, TRAINED_MODEL_PATH, MODELS_DIR, DATA_DIR

def _check_and_download_nltk_resources():
    """
    Checks if necessary NLTK resources are available and downloads them if not.
    """
    resources = ['stopwords', 'punkt', 'porter']
    print("Checking NLTK resources...")
    for resource in resources:
        try:
            nltk.data.find(f'corpora/{resource}')
            print(f"  NLTK resource '{resource}' found.")
        except nltk.downloader.DownloadError:
            print(f"  Downloading NLTK resource: {resource}...")
            try:
                nltk.download(resource, quiet=True) # Use quiet=True to avoid verbose output
                print(f"  NLTK resource '{resource}' downloaded.")
            except Exception as e:
                print(f"  Failed to download NLTK resource '{resource}': {e}")
                print("  Please try running 'python -m nltk.downloader all' from your terminal.")
                exit(1) # Exit if critical resources cannot be downloaded

def run_training_pipeline():
    """
    Executes the full training pipeline: loads data, preprocesses, trains, and saves the model.
    """
    print("\n--- Starting Model Training Pipeline ---")

    # Ensure data directory exists and prompt to place dataset
    # config.py already creates these directories on import, but this adds user guidance
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True) # Added exist_ok for robustness
        print(f"Created data directory at: {DATA_DIR}")
    
    if not os.path.exists(SPAM_DATASET_PATH):
        print(f"Dataset not found at '{SPAM_DATASET_PATH}'.")
        print("Please download the 'spam.csv' dataset (e.g., from Kaggle: SMS Spam Collection Dataset)")
        print(f"and place it in the '{DATA_DIR}' directory.")
        return False # Indicate that training couldn't proceed

    df = load_dataset(SPAM_DATASET_PATH)
    if df.empty:
        print("Failed to load dataset. Training aborted.")
        return False

    # Apply preprocessing to the 'text' column
    print("Applying text preprocessing to dataset...")
    df['processed_text'] = df['text'].apply(preprocess_text)
    
    # Use the processed text for training
    df_for_training = df[['processed_text', 'label']].rename(columns={'processed_text': 'text'})

    model_pipeline = train_model(df_for_training)
    if model_pipeline:
        save_model(model_pipeline, TRAINED_MODEL_PATH)
        print("--- Model Training Pipeline Completed ---")
        return True
    else:
        print("--- Model Training Pipeline Failed ---")
        return False

def predict_email_spam(model):
    """
    Provides an interactive interface for classifying new email texts.

    Args:
        model: The loaded trained machine learning model.
    """
    if model is None:
        print("\nError: Model is not loaded. Please train the model first.")
        return

    print("\n--- Email Spam Classifier ---")
    print("Enter 'exit' to quit.")

    while True:
        email_input = input("\nEnter email text to classify: ")
        if email_input.lower() == 'exit':
            print("Exiting email classifier.")
            break
        
        if not email_input.strip():
            print("Please enter some text.")
            continue

        result = classify_email(email_input, model)
        print(f"The email is classified as: {result}")

def main():
    """
    Main function to run the Email Spam Classifier application.
    Checks for NLTK resources, trains model if not available, and runs prediction.
    """
    print("--- Welcome to the Email Spam Classifier ---")

    _check_and_download_nltk_resources()
    
    # Check if the model exists, otherwise train it
    if not os.path.exists(TRAINED_MODEL_PATH):
        print("\nNo trained model found. Initiating training pipeline...")
        training_successful = run_training_pipeline()
        if not training_successful:
            print("Application cannot proceed without a trained model. Exiting.")
            return
    else:
        print(f"\nTrained model found at '{TRAINED_MODEL_PATH}'. Loading existing model.")

    # Load the model
    model = load_model(TRAINED_MODEL_PATH)

    # If model loaded successfully, start prediction interface
    if model:
        predict_email_spam(model)
    else:
        print("Failed to load model. Please ensure the model is trained or troubleshoot issues.")

if __name__ == "__main__":
    main()
