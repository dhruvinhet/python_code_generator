import transformers
import torch
from transformers.pipelines.text_classification import TextClassificationPipeline

def load_sentiment_model():
    """
    Loads a pre-trained sentiment analysis model from the Hugging Face Transformers library.
    
    This function attempts to load a common sentiment analysis model and determines
    whether to use a GPU (CUDA) or CPU based on availability.

    Returns:
        transformers.pipelines.text_classification.TextClassificationPipeline:
            The loaded sentiment analysis pipeline.
    
    Raises:
        Exception: If there is an error during model loading.
    """
    # Using a common sentiment analysis model fine-tuned for SST-2
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    try:
        # Determine device: 0 for GPU (CUDA), -1 for CPU
        if torch.cuda.is_available():
            device = 0
            print("Using CUDA for sentiment analysis.")
        else:
            device = -1
            print("Using CPU for sentiment analysis.")

        # Initialize the sentiment analysis pipeline
        # The `tokenizer` argument ensures the correct tokenizer for the model is loaded.
        sentiment_pipeline = transformers.pipeline(
            "sentiment-analysis",
            model=model_name,
            tokenizer=model_name,
            device=device  # Assign the device to the pipeline
        )
        return sentiment_pipeline
    except Exception as e:
        # Log the error and re-raise to be handled by the calling application
        print(f"Error loading sentiment model: {e}")
        raise

def analyze_sentiment(text: str, sentiment_pipeline: TextClassificationPipeline) -> dict:
    """
    Analyzes the sentiment of the provided text using the pre-loaded sentiment analysis pipeline.

    Args:
        text (str): The input text to analyze.
        sentiment_pipeline: The pre-loaded sentiment analysis pipeline instance.

    Returns:
        dict: A dictionary containing the sentiment label (e.g., 'POSITIVE', 'NEGATIVE')
              and the confidence score. Example: {'label': 'POSITIVE', 'score': 0.9998}.
              Includes 'message' key for error or empty input cases.
    """
    if not text or not text.strip():
        return {"label": "N/A", "score": 0.0, "message": "Please enter some text to analyze."}

    try:
        # The pipeline processes the text and returns a list of results.
        # For a single text input, it returns a list with one dictionary.
        result = sentiment_pipeline(text)[0]
        return result
    except Exception as e:
        # Catch any errors during analysis and return an error message
        print(f"Error analyzing sentiment: {e}")
        return {"label": "Error", "score": 0.0, "message": f"An error occurred during analysis: {e}"}
