import streamlit as st
from sentiment_utils import analyze_sentiment_textblob


def main():
    st.title("Sentiment Analyzer")

    user_input = st.text_area("Enter text for sentiment analysis:", "")

    if user_input:
        try:
            sentiment_score = analyze_sentiment_textblob(user_input)

            st.write(f"Sentiment Score: {sentiment_score:.2f}")

            if sentiment_score > 0.2:
                st.success("Positive Sentiment")
            elif sentiment_score < -0.2:
                st.error("Negative Sentiment")
            else:
                st.info("Neutral Sentiment")
        except Exception as e:
            st.error(f"An error occurred during sentiment analysis: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred in the main function: {e}")