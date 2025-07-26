# main.py
import streamlit as st
import random
from game_logic import create_board, reveal_tile, calculate_multiplier, is_game_over, is_board_complete



def main():
    """Orchestrates the Minesweeper Gambling game using Streamlit for the UI."""
    st.title("Minesweeper Gambling")

    # Initialize session state if it doesn't exist
    if 'board' not in st.session_state:
        st.session_state.board = None
    if 'revealed' not in st.session_state:
        st.session_state.revealed = None
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'multiplier' not in st.session_state:
        st.session_state.multiplier = 1.0
    if 'bet_amount' not in st.session_state:
        st.session_state.bet_amount = 10.0  # Default bet amount
    if 'rows' not in st.session_state:
        st.session_state.rows = 5
    if 'cols' not in st.session_state:
        st.session_state.cols = 5
    if 'bombs' not in st.session_state:
        st.session_state.bombs = 5
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False

    # Sidebar for game settings
    with st.sidebar:
        st.header("Game Settings")
        st.session_state.rows = st.number_input("Rows:", min_value=3, max_value=10, value=st.session_state.rows)
        st.session_state.cols = st.number_input("Columns:", min_value=3, max_value=10, value=st.session_state.cols)
        st.session_state.bombs = st.number_input("Bombs:", min_value=1, max_value=st.session_state.rows * st.session_state.cols - 1, value=st.session_state.bombs)
        st.session_state.bet_amount = st.number_input("Bet Amount:", min_value=1.0, value=st.session_state.bet_amount)

        if st.button("New Game"):
            try:
                if st.session_state.rows * st.session_state.cols <= st.session_state.bombs:
                    st.error("Number of bombs exceeds the number of tiles. Please reduce the number of bombs.")
                    st.stop()

                st.session_state.board = create_board(st.session_state.rows, st.session_state.cols, st.session_state.bombs)
                st.session_state.revealed = [[False for _ in range(st.session_state.cols)] for _ in range(st.session_state.rows)]
                st.session_state.game_over = False
                st.session_state.multiplier = 1.0
                st.session_state.game_started = True
            except Exception as e:
                st.error(f"An error occurred while creating the game: {e}")

    # Game board display
    if not st.session_state.game_started:
        st.info("Click 'New Game' to start.")
    else:
        st.write(f"Multiplier: {st.session_state.multiplier:.2f}")
        game_won = False
        for i in range(st.session_state.rows):
            cols = st.columns(st.session_state.cols)
            for j in range(st.session_state.cols):
                if st.session_state.revealed[i][j]:
                    if st.session_state.board[i][j] == -1:  # Bomb
                        cols[j].write(":bomb:")
                    else:
                        cols[j].write(":diamond:")
                else:
                    if not st.session_state.game_over:
                        button_key = f"{i}-{j}"
                        if cols[j].button(" ", key=button_key):
                            try:
                                result = reveal_tile(st.session_state.board, st.session_state.revealed, i, j)
                                if result == "bomb":
                                    st.session_state.game_over = True
                                    st.error("Game Over! You hit a bomb.")
                                elif result == "diamond":
                                    st.session_state.multiplier = calculate_multiplier(st.session_state.revealed, st.session_state.board)
                                    #st.rerun()
                                if is_board_complete(st.session_state.board, st.session_state.revealed):
                                    st.success("Congratulations! You won!")
                                    st.write(f"Final Winnings: {st.session_state.bet_amount * st.session_state.multiplier:.2f}")
                                    st.session_state.game_over = True

                                st.experimental_rerun()

                            except Exception as e:
                                st.error(f"An error occurred during the game: {e}")
                    else:
                        cols[j].write(" ")

        if st.session_state.game_over:
            st.write(f"Final Winnings: {st.session_state.bet_amount * st.session_state.multiplier:.2f} (Game Over)")


# Run the Streamlit app
if __name__ == "__main__":
    main()
