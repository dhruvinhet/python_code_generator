import streamlit as st
import pandas as pd
import random
from mcq_data import get_all_questions 
from utils import initialize_session_state, shuffle_options, update_score

def display_question_page():
    """
    Displays the current question, its options, and handles user input for answering.
    Manages progression to the next question or quiz completion.
    """
    st.title("General Knowledge MCQ Practice")

    # Ensure session state is initialized before accessing it
    initialize_session_state()

    questions = st.session_state.questions
    current_index = st.session_state.current_question_index

    if current_index < len(questions):
        question_data = questions[current_index]
        st.header(f"Question {current_index + 1}/{len(questions)}")
        st.write(f"**{question_data['question']}**")

        # Shuffle options only once per question display or on first load
        if current_index not in st.session_state.shuffled_options:
            st.session_state.shuffled_options[current_index] = shuffle_options(question_data['options'])
        
        selected_option = st.radio(
            "Choose your answer:",
            st.session_state.shuffled_options[current_index],
            key=f"q_{current_index}" # Unique key for the radio button to prevent re-selection issues
        )

        st.markdown("---")

        if st.button("Next Question", key=f"next_q_btn_{current_index}"):
            # st.radio always has a selected option (defaults to the first if not clicked),
            # so 'selected_option' will always be a truthy value from the options list.
            # The 'else: st.warning("Please select an answer before proceeding.")' block
            # is unreachable and thus removed.
            is_correct = (selected_option == question_data['answer'])
            update_score(is_correct)
            
            # Store user's answer and correct answer for result page review
            st.session_state.user_answers.append({
                "question_idx": current_index,
                "question_text": question_data['question'],
                "user_answer": selected_option,
                "correct_answer": question_data['answer'],
                "is_correct": is_correct
            })

            st.session_state.current_question_index += 1
            # If all questions are answered, mark quiz as completed
            if st.session_state.current_question_index >= len(questions):
                st.session_state.quiz_completed = True
            
            # Rerun the app to show the next question or results page
            st.experimental_rerun()
    else:
        # This branch ensures that if current_index somehow exceeds questions length,
        # the quiz is marked as completed and results are shown.
        st.session_state.quiz_completed = True
        st.experimental_rerun()

def display_result_page():
    """
    Displays the final score and a summary of all questions, user's answers,
    and correct answers. Provides an option to restart the quiz.
    """
    st.title("Quiz Results")
    total_questions = len(st.session_state.questions)
    score = st.session_state.score

    st.success(f"You scored {score} out of {total_questions} questions!")
    st.write("---")
    st.subheader("Detailed Review")

    # Display results using Pandas DataFrame for better visualization and readability
    results_df_data = []
    for ua in st.session_state.user_answers:
        status = "Correct" if ua["is_correct"] else "Incorrect"
        results_df_data.append({
            "Question": ua["question_text"],
            "Your Answer": ua["user_answer"],
            "Correct Answer": ua["correct_answer"],
            "Status": status
        })
    
    results_df = pd.DataFrame(results_df_data)
    st.dataframe(results_df, use_container_width=True)

    st.write("---")
    if st.button("Restart Quiz"):
        # Reset specific session state variables to start a new quiz
        # Deleting all keys and re-initializing ensures a clean slate, including new question order
        for key in st.session_state.keys():
            del st.session_state[key]
        initialize_session_state() # Re-initialize to load new questions/reset state
        st.experimental_rerun() # Rerun to display the first question of the new quiz

def main_app_flow():
    """
    Controls the main application flow, switching between question display and result display
    based on the quiz completion status.
    """
    initialize_session_state() # Ensure session state is always initialized at the start of the app flow

    if st.session_state.quiz_completed:
        display_result_page()
    else:
        display_question_page()

# This check ensures that main_app_flow() is called when the script is run.
# For Streamlit, the entire script is run on each interaction, so calling it directly
# at the top-level scope is common. The `if __name__ == "__main__":` block adds
# robustness for standalone execution or testing outside of `streamlit run`.
if __name__ == "__main__":
    main_app_flow()
