# streamlit_ui.py
import streamlit as st
import tictactoe


def display_board(board):
    """Displays the Tic-Tac-Toe board using Streamlit buttons."""
    cols = st.columns(3)
    move = None
    for i in range(3):
        for j in range(3):
            index = i * 3 + j
            with cols[j]:
                button_key = f"button_{index}"
                if st.session_state[f"board_{index}"] == ' ':
                    if st.button(" ", key=button_key):
                        move = index # Capture move, but don't return immediately
                else:
                    st.button(st.session_state[f"board_{index}"], disabled=True, key=button_key)
    return move # Return move after all buttons are processed.


def get_player_move(board):
    """Gets the player's move from the Streamlit UI."""
    move = display_board(board)
    return move


def display_game_over(winner):
    """Displays the game over message using Streamlit."""
    if winner == tictactoe.PLAYER:
        st.success("You win!")
    elif winner == tictactoe.AI:
        st.error("AI wins!")
    else:
        st.info("It's a draw!")


def reset_game():
    """Resets the game state in Streamlit session state."""
    for i in range(9):
        st.session_state[f"board_{i}"] = ' '
    st.session_state.game_over = False
    st.session_state.board = tictactoe.initialize_board()
    update_board_state(st.session_state.board) # Update the UI after reset.


def update_board_state(board):
    """Updates the streamlit session state to reflect the game board"""
    for i in range(9):
        st.session_state[f"board_{i}"] = board[i]
