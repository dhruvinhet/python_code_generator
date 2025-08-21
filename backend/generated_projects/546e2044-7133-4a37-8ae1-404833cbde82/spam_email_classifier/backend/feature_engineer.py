import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import logging

nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def engineer_features(df, method='tfidf'):
    """Engineers features from text data.

    Args:
        df (pandas.DataFrame): The DataFrame containing text data.
        method (str, optional): Feature extraction method ('tfidf' or 'embeddings'). Defaults to 'tfidf'.

    Returns:
        pandas.DataFrame or scipy.sparse.csr.csr_matrix: The DataFrame with added features or a sparse matrix if using TF-IDF.
    """
    try:
        logging.info(f"Engineering features using {method} method...")
        text_data = df['email_body'] #You might need to adjust this based on your columns
        stop_words = set(stopwords.words('english'))
        stemmer = PorterStemmer()
        
        if method == 'tfidf':
            vectorizer = TfidfVectorizer(stop_words=stop_words, preprocessor=lambda x: ' '.join([stemmer.stem(word) for word in nltk.word_tokenize(x) if word.isalnum() and word not in stop_words]))
            features = vectorizer.fit_transform(text_data)
            logging.info("TF-IDF features created.")
            return features
        elif method == 'embeddings':
            model = SentenceTransformer('all-mpnet-base-v2')
            embeddings = model.encode(text_data)
            df['embeddings'] = embeddings.tolist()
            logging.info("Sentence embeddings created.")
            return df
        else:
            logging.error(f"Unsupported feature extraction method: {method}")
            return None
    except Exception as e:
        logging.error(f"An error occurred during feature engineering: {e}")
        return None