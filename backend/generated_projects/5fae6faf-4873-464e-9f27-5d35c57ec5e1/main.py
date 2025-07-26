# main.py
import streamlit as st
import random
from game_logic import play_game, validate_bet

# Configuration
STARTING_BALANCE = 100

# Function to display game rules
def display_rules():
    st.markdown("""
    **Unlucky Streak: A Game of Unfavorable Odds**

    Welcome to Unlucky Streak, a simple gambling game where the odds are intentionally stacked against you!

    **How to Play:**
    1.  Enter the amount you want to bet.
    2.  Click the 'Play' button.
    3.  See if you win or lose (hint: you'll probably lose).
    4.  Continue until you run out of money or get lucky.

    **Rules:**
    *   You start with a balance of $100.
    *   The bet amount must be a positive number and cannot exceed your current balance.
    *   The game is designed to have a lower probability of winning.
    *   Have fun (or try to)!
    """)

# Main function to handle the Streamlit app flow
def main():
    st.title("Unlucky Streak")

    # Initialize session state variables if they don't exist
    if 'balance' not in st.session_state:
        st.session_state['balance'] = STARTING_BALANCE

    if 'game_count' not in st.session_state:
        st.session_state['game_count'] = 0

    display_rules()

    # Display current balance
    st.write(f"Current Balance: ${st.session_state['balance']:.2f}")
    st.write(f"Games Played: {st.session_state['game_count']}")

    # User input for bet amount
    bet_amount = st.number_input("Enter your bet amount:", min_value=0.01, max_value=st.session_state['balance'], step=0.01)

    # Play button
    if st.button("Play"):
        # Validate the bet
        if not validate_bet(bet_amount, st.session_state['balance']):
            st.error("Invalid bet amount. Please enter a bet between $0.01 and your current balance.")
        else:
            try:
                # Play the game and update the balance
                result, win_amount = play_game(bet_amount)
                st.session_state['game_count'] += 1

                if result == "win":
                    st.success(f"Congratulations! You won ${win_amount:.2f}")
                    st.session_state['balance'] += win_amount
                else:
                    st.error(f"Sorry, you lost ${bet_amount:.2f}")
                    st.session_state['balance'] -= bet_amount

                # Display updated balance
                st.write(f"New Balance: ${st.session_state['balance']:.2f}")

                # Check if the player is bankrupt
                if st.session_state['balance'] <= 0:
                    st.warning("You're broke! Game over.")

                # Display a fun losing quote.
                losing_quotes = [
                    "Better luck next time (just kidding, probably not).",
                    "Well, that was anticlimactic.",
                    "Don't worry, you'll get it next time. (Narrator: They wouldn't.)",
                    "The house always wins.",
                    "Maybe gambling isn't for you?",
                    "At least you tried!",
                ]

                if result == 'lose':
                    st.write(random.choice(losing_quotes))
            except Exception as e:
                st.error(f"An error occurred: {e}")


# Run the main function only when the script is executed directly
if __name__ == "__main__":
    main()