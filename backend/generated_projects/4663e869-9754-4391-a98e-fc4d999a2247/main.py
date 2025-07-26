# main.py
import streamlit as st
import time
from text_generator import generate_text
from typing_test import calculate_wpm, calculate_accuracy, display_results

# Streamlit app title
st.title("Typing Speed Test")

# Initialize session state variables if they don't exist
if 'test_running' not in st.session_state:
    st.session_state.test_running = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'text' not in st.session_state:
    st.session_state.text = ""
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'wpm' not in st.session_state:
    st.session_state.wpm = 0
if 'accuracy' not in st.session_state:
    st.session_state.accuracy = 0


# Function to handle starting the test
def start_typing_test():
    st.session_state.text = generate_text(200) # generate the text
    st.session_state.test_running = True  # Set the test_running state to true when the start button is clicked
    st.session_state.start_time = time.time() #Record the current time
    st.session_state.user_input = ""


# Display the text to be typed
st.write("Type the following text:")
st.info(st.session_state.text)

# Text area for user input
user_input = st.text_area("Your input:", key="user_input", disabled=not st.session_state.test_running, height=150)

# Start/Restart button
col1, col2 = st.columns(2)
with col1:
    if not st.session_state.test_running:
        if st.button("Start Typing Test"):
            start_typing_test()
    else:
        if st.button("Restart Typing Test"):
            start_typing_test()

# Check if the test is running and the user has entered the entire text
if st.session_state.test_running:
    if st.session_state.text and user_input:
        if len(user_input) >= len(st.session_state.text):
            # Calculate time taken
            time_taken = time.time() - st.session_state.start_time

            # Calculate words per minute (WPM)
            st.session_state.wpm = calculate_wpm(st.session_state.text, time_taken)

            # Calculate accuracy
            st.session_state.accuracy = calculate_accuracy(st.session_state.text, user_input)

            # Display results
            st.success("Test Complete!")
            display_results(st.session_state.wpm, st.session_state.accuracy)

            # Reset test state
            st.session_state.test_running = False

    elif st.session_state.text and not user_input:
        st.warning("Start typing to see results.")

# Run only when streamlit is active.
if __name__ == '__main__':
    pass