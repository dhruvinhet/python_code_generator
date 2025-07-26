# main.py
import streamlit as st
import nltk
from sentiment_utils import initialize_sentiment_analyzer, get_sentiment_score

# Download necessary NLTK data (only needs to be done once)
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')


# Initialize the sentiment analyzer
analyzer = initialize_sentiment_analyzer()


def analyze_sentiment(text):
    """Takes text input and returns sentiment score (positive, negative, neutral, compound)."""
    return get_sentiment_score(text, analyzer)


def main():
    """The main function to run the Streamlit application."""
    st.title("Sentiment Analyzer")
    st.write("Enter text below to analyze its sentiment.")

    user_input = st.text_area("Enter Text:", "")

    if user_input:
        # Analyze the sentiment of the user input
        sentiment_scores = analyze_sentiment(user_input)

        # Display the sentiment scores
        st.subheader("Sentiment Analysis Results:")
        st.write(f"Positive: {sentiment_scores['pos']:.3f}")
        st.write(f"Negative: {sentiment_scores['neg']:.3f}")
        st.write(f"Neutral: {sentiment_scores['neu']:.3f}")
        st.write(f"Compound: {sentiment_scores['compound']:.3f}")

        # Determine overall sentiment based on compound score
        if sentiment_scores['compound'] >= 0.05:
            st.write("**Overall Sentiment: Positive**")
        elif sentiment_scores['compound'] <= -0.05:
            st.write("**Overall Sentiment: Negative**")
        else:
            st.write("**Overall Sentiment: Neutral**")


# Run the Streamlit application
if __name__ == "__main__":
    main()