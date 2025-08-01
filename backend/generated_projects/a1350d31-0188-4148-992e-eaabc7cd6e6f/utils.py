import streamlit as st
import random
from mcq_data import get_all_questions # Import function to load questions

def initialize_session_state():
    """
    Initializes necessary variables in Streamlit's session state if they don't exist.
    This ensures the quiz state (questions, current index, score, user answers,
    and quiz completion status) is maintained across Streamlit reruns.
    """
    if 'questions' not in st.session_state:
        # Load questions at the start of the session or quiz restart
        st.session_state.questions = get_all_questions()
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'user_answers' not in st.session_state:
        # Stores a list of dictionaries to track user's answers and correctness
        # e.g., [{"question_idx": X, "question_text": "...", "user_answer": "Y", "correct_answer": "Z", "is_correct": True}]
        st.session_state.user_answers = []
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'shuffled_options' not in st.session_state:
        # Cache for shuffled options for each question to ensure consistency during a question display
        st.session_state.shuffled_options = {}

def shuffle_options(options_list):
    """
    Shuffles a list of options randomly and returns the shuffled list.
    This is used to randomize the order of answer choices for each question.
    Args:
        options_list (list): A list of strings representing answer options for a question.
    Returns:
        list: The randomly shuffled list of options.
    """
    shuffled = options_list[:] # Create a shallow copy to avoid modifying the original list in place
    random.shuffle(shuffled)
    return shuffled

def update_score(is_correct):
    """
    Updates the user's score based on whether the answer provided was correct.
    The score is stored in Streamlit's session state.
    Args:
        is_correct (bool): True if the user's answer was correct, False otherwise.
    """
    if is_correct:
        st.session_state.score += 1
