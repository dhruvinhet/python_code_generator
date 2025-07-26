# main.py
import streamlit as st
import time

from utils import generate_random_words


def calculate_wpm(text, input_text, start_time, end_time):
    """Calculates words per minute (WPM)."""
    if start_time is None or end_time is None:
        return 0
    time_taken = end_time - start_time
    if time_taken == 0:
        return 0  # Avoid division by zero
    words_typed = len(input_text.split())  # Count words in entered text
    wpm = (words_typed / time_taken) * 60
    return round(wpm)


def display_test_interface():
    """Displays the typing test interface using Streamlit.
    Includes the text to type, input box, and calculates/displays WPM.
    """
    st.write("Type the following text:")
    st.info(st.session_state['text'])

    user_input = st.text_area("Start typing here:", value=st.session_state['input_text'], height=150, disabled=not st.session_state['test_running'])
    st.session_state['input_text'] = user_input

    if not st.session_state['test_running']:
        if st.button("Start Test"):
            st.session_state['start_time'] = time.time()
            st.session_state['test_running'] = True
            st.experimental_rerun()  # Force streamlit to refresh the app

    # Check if the test is running AND the input text matches the expected text
    if st.session_state['test_running'] and st.session_state['input_text'].strip() == st.session_state['text'].strip():
        st.session_state['end_time'] = time.time()
        st.session_state['wpm'] = calculate_wpm(st.session_state['text'], st.session_state['input_text'],
                                                 st.session_state['start_time'], st.session_state['end_time'])
        st.success(f"Congratulations! Your WPM is: {st.session_state['wpm']}")
        st.session_state['test_running'] = False  # Stop the test

        if st.button("Restart Test"):
            reset_state()
            st.experimental_rerun()

    elif not st.session_state['test_running'] and st.session_state['wpm'] > 0:
        st.write(f"Your WPM was: {st.session_state['wpm']}")


def reset_state():
    """Resets the session state to start a new test."""
    st.session_state['start_time'] = None
    st.session_state['text'] = generate_random_words(20)
    st.session_state['input_text'] = ''
    st.session_state['wpm'] = 0
    st.session_state['test_running'] = False


def main():
    """Main function to run the Streamlit application."""
    st.title("Typing Speed Test")
    display_test_interface()


# Initialize session state
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = None
if 'text' not in st.session_state:
    st.session_state['text'] = generate_random_words(20)
if 'input_text' not in st.session_state:
    st.session_state['input_text'] = ''
if 'wpm' not in st.session_state:
    st.session_state['wpm'] = 0
if 'test_running' not in st.session_state:
    st.session_state['test_running'] = False

# Run the app
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {e}")
