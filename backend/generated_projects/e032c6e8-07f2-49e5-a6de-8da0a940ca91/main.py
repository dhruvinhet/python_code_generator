import streamlit as st
import sentiment_analyzer # Import the module containing sentiment analysis logic

def run_app():
    """
    Runs the Streamlit application for text sentiment analysis.
    This function sets up the UI, handles user input, triggers sentiment analysis,
    and displays the results.
    """
    # Configure Streamlit page settings
    st.set_page_config(page_title="Streamlit Text Sentiment Analyzer", layout="centered")

    # Application title and description
    st.title("Sentiment Analyzer \ud83d\udcac")
    st.write("Enter text below to get its sentiment (positive or negative) using a pre-trained model.")

    # Use st.cache_resource to load the model only once across multiple app reruns.
    # This is crucial for performance with large models.
    @st.cache_resource
    def get_sentiment_pipeline():
        """
        Loads and caches the sentiment analysis pipeline using st.cache_resource.
        This function is designed to run only once during the app's lifetime.
        """
        with st.spinner("Loading sentiment model... This might take a moment."):
            try:
                pipeline = sentiment_analyzer.load_sentiment_model()
                st.success("Sentiment model loaded successfully!")
                return pipeline
            except Exception as e:
                st.error(f"Failed to load sentiment model: {e}\\nPlease ensure all dependencies are installed.")
                # Halt the app execution if the model cannot be loaded
                st.stop()

    # Get the sentiment pipeline. It will be loaded/cached on first run.
    sentiment_pipeline = get_sentiment_pipeline()

    # Text area for user input
    user_input = st.text_area(
        "Enter text here:",
        placeholder="Type something to analyze its sentiment... e.g., 'I love this product!'",
        height=150,
        key="user_text_input"
    )

    # Analyze button
    if st.button("Analyze Sentiment", key="analyze_button"):
        if user_input:
            with st.spinner("Analyzing sentiment..."):
                # Call the sentiment analysis function from the imported module
                result = sentiment_analyzer.analyze_sentiment(user_input, sentiment_pipeline)

                # Display results based on the analysis outcome
                if result.get("label") == "Error":
                    st.error(result.get("message", "An unknown error occurred during analysis."))
                elif result.get("label") == "N/A":
                    st.warning(result.get("message", "No text provided for analysis."))
                else:
                    # Extract label and score from the result
                    label = result["label"]
                    score = result["score"]

                    st.subheader("Analysis Result:")
                    # Display sentiment with appropriate styling
                    if label == "POSITIVE":
                        st.success(f"Sentiment: Positive \ud83d\ude0a (Confidence: {score:.2f})")
                    elif label == "NEGATIVE":
                        st.error(f"Sentiment: Negative \ud83d\ude20 (Confidence: {score:.2f})")
                    else:
                        # Handle other labels if the model returns them (e.g., 'NEUTRAL')
                        st.info(f"Sentiment: {label} (Confidence: {score:.2f})")

                    st.write(f"Raw Model Output: {result}")
        else:
            st.warning("Please enter some text to analyze before clicking the button.")

def main():
    """
    Main entry point of the Streamlit application.
    This function acts as a wrapper for `run_app()`.
    Streamlit applications are typically run using `streamlit run <your_script.py>`,
    and Streamlit handles the execution context. Therefore, directly calling `run_app()`
    within `if __name__ == "__main__"` block is the standard practice.
    """
    run_app()

# Standard Python entry point check
if __name__ == "__main__":
    main()
