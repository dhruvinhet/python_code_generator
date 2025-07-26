# typing_test.py
import streamlit as st

# Function to calculate words per minute (WPM)
def calculate_wpm(text, time_taken):
    """Calculates the words per minute (WPM).

    Args:
        text (str): The text that was typed.
        time_taken (float): The time taken to type the text in seconds.

    Returns:
        float: The words per minute (WPM).
    """
    try:
        word_count = len(text.split())
        wpm = (word_count / time_taken) * 60
        return round(wpm, 2)
    except ZeroDivisionError:
        return 0  # Handle case where no time has elapsed


# Function to calculate accuracy
def calculate_accuracy(text, user_input):
    """Calculates the accuracy of the typing test.

    Args:
        text (str): The text that was supposed to be typed.
        user_input (str): The text that the user typed.

    Returns:
        float: The accuracy of the typing test as a percentage.
    """
    correct_characters = 0
    min_length = min(len(text), len(user_input))
    for i in range(min_length):
        if text[i] == user_input[i]:
            correct_characters += 1

    try:
        accuracy = (correct_characters / len(text)) * 100
        return round(accuracy, 2)
    except ZeroDivisionError:
        return 0  # Handle case where the text is empty
    except Exception as e:
        st.error(f"An error occurred during accuracy calculation: {e}")
        return 0


# Function to display the results
def display_results(wpm, accuracy):
    """Displays the results of the typing test.

    Args:
        wpm (float): The words per minute (WPM).
        accuracy (float): The accuracy of the typing test.
    """
    st.write(f"Words Per Minute: {wpm}")
    st.write(f"Accuracy: {accuracy}%")

if __name__ == '__main__':
    #Example Use (optional)
    sample_text = "This is a sample text for testing the typing speed test application."
    user_text = "This is a smaple text for testing the typing speed test applicaiton."
    time_taken = 10
    wpm = calculate_wpm(sample_text,time_taken)
    accuracy = calculate_accuracy(sample_text,user_text)
    print(f"WPM {wpm}")
    print(f"Accuracy {accuracy}")