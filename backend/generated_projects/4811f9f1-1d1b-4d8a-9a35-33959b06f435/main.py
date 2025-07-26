# Import necessary libraries
import streamlit as st
import random


def generate_random_number():
    """Generates a random integer between 1 and 100 (inclusive).

    Returns:
        int: A random integer.
    """
    return random.randint(1, 100)


def check_guess(guess, number, attempts_remaining):
    """Checks the user's guess against the random number and provides feedback.

    Args:
        guess (int): The user's guess.
        number (int): The random number to guess.
        attempts_remaining (int): The number of attempts remaining.

    Returns:
        str: A message indicating whether the guess is too high, too low, or correct.
    """
    if guess > number:
        return f"Too high! Attempts remaining: {attempts_remaining}"
    elif guess < number:
        return f"Too low! Attempts remaining: {attempts_remaining}"
    else:
        return f"Congratulations! You guessed the number in {st.session_state.max_attempts - attempts_remaining} attempts!"


def main():
    """Main function to run the Streamlit number guessing game.

    This function initializes the game state using Streamlit's session state,
    takes user input, and provides feedback on their guesses.
    """
    st.title("Number Guessing Game")

    # Initialize session state variables if they don't exist
    if 'number' not in st.session_state:
        st.session_state.number = generate_random_number()
        st.session_state.attempts = 0
        st.session_state.max_attempts = 7  # Set maximum attempts
        st.session_state.game_over = False  # Game Status

    # Display number of attempts remaining
    st.write(f"Attempts remaining: {st.session_state.max_attempts - st.session_state.attempts}")

    # Get user's guess from a text input
    if not st.session_state.game_over:
        guess = st.number_input("Enter your guess (between 1 and 100):", min_value=1, max_value=100, step=1)

        # Check the guess when the user clicks the 'Guess' button
        if st.button("Guess"): #and not st.session_state.game_over: #removed redundant check
            if guess:
                try:
                    guess = int(guess)
                    if 1 <= guess <= 100:
                        st.session_state.attempts += 1
                        attempts_remaining = st.session_state.max_attempts - st.session_state.attempts

                        # Check if the user has exceeded the maximum attempts
                        if attempts_remaining >= 0: #Changed to >= 0 for correct logic
                            message = check_guess(guess, st.session_state.number, attempts_remaining)
                            st.write(message)
                            if "Congratulations" in message:
                                st.session_state.game_over = True  # End Game
                        else:
                            st.write(f"You ran out of attempts. The number was {st.session_state.number}.")
                            st.session_state.game_over = True  # End Game
                            st.write("Game over. Please refresh to play again.")

                    else:
                        st.warning("Please enter a number between 1 and 100.")
                except ValueError:
                    st.error("Invalid input. Please enter a valid integer.")
    else:
        st.write("Game over. Please refresh to play again.")


# Run the main function when the script is executed directly
if __name__ == "__main__":
    main()