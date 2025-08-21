# data_loader.py

"""
Happens loading of email datasets and performs initial text preprocessing.
Includes functions for loading data from CSV and cleaning/tokenizing text.
"""

import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# NLTK resources will be checked and downloaded by main.py
# Initialize NLTK components globally within the module for efficiency
STOP_WORDS = set(stopwords.words('english'))
PORTER_STEMMER = PorterStemmer()

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Loads an email dataset from a CSV file.
    Expects a CSV with at least two columns, typically 'v1' for labels and 'v2' for text.

    Args:
        file_path (str): The path to the CSV dataset file.

    Returns:
        pd.DataFrame: A DataFrame with 'label' and 'text' columns.
                      Returns an empty DataFrame if loading fails.
    """
    try:
        # Load the dataset, assuming 'v1' is label and 'v2' is text, common for spam datasets
        df = pd.read_csv(file_path, encoding='latin-1')
        df = df.iloc[:, :2] # Take only the first two columns
        df.columns = ['label', 'text'] # Rename columns for clarity

        # Map 'v1' column (labels) to binary values if not already
        df['label'] = df['label'].map({'ham': 0, 'spam': 1})

        print(f"Dataset loaded successfully from {file_path}. Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: Dataset file not found at {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred while loading the dataset: {e}")
        return pd.DataFrame()

def preprocess_text(text: str) -> str:
    """
    Performs text preprocessing: lowercasing, removing non-alphabetic characters,
    tokenization, stop word removal, and stemming.

    Args:
        text (str): The raw input text (e.g., an email body).

    Returns:
        str: The cleaned and preprocessed text, ready for feature extraction.
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove non-alphabetic characters (keep spaces)
    text = re.sub(r'[^a-z\\s]', '', text)
    
    # Tokenize text
    words = word_tokenize(text)
    
    # Remove stop words and perform stemming
    processed_words = [
        PORTER_STEMMER.stem(word)
        for word in words
        if word not in STOP_WORDS
    ]
    
    # Join back into a single string
    return " ".join(processed_words)
