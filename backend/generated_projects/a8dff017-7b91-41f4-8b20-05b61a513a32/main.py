# main.py
import streamlit as st
import streamlit_ui
import tictactoe


def main():
    st.title("Tic-Tac-Toe vs AI")

    # Initialize session state
    if 'board' not in st.session_state:
        st.session_state.board = tictactoe.initialize_board()
        streamlit_ui.update_board_state(st.session_state.board)
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'ai_turn' not in st.session_state:
        st.session_state.ai_turn = False  # Add a flag to control the AI's turn

    # Reset button
    if st.button("Reset Game"):
        streamlit_ui.reset_game()
        st.session_state.ai_turn = False

    # Game loop
    if not st.session_state.game_over:
        # Player's turn
        if not st.session_state.ai_turn:
            player_move = streamlit_ui.get_player_move(st.session_state.board)

            if player_move is not None:
                if st.session_state.board[player_move] == ' ':
                    if tictactoe.make_move(st.session_state.board, player_move, tictactoe.PLAYER):
                        streamlit_ui.update_board_state(st.session_state.board)

                        if tictactoe.is_winner(st.session_state.board, tictactoe.PLAYER):
                            st.session_state.game_over = True
                            streamlit_ui.display_game_over(tictactoe.PLAYER)
                        elif tictactoe.is_board_full(st.session_state.board):
                            st.session_state.game_over = True
                            streamlit_ui.display_game_over(None)
                        else:
                            st.session_state.ai_turn = True  # Switch to AI's turn
                            st.rerun() #Force streamlit to update
                else:
                     st.warning("That spot is already taken. Please choose another.")

        # AI's turn
        if st.session_state.ai_turn and not st.session_state.game_over:
            ai_move = tictactoe.get_ai_move(st.session_state.board)
            if ai_move is not None:
                if tictactoe.make_move(st.session_state.board, ai_move, tictactoe.AI):
                    streamlit_ui.update_board_state(st.session_state.board)

                    if tictactoe.is_winner(st.session_state.board, tictactoe.AI):
                        st.session_state.game_over = True
                        streamlit_ui.display_game_over(tictactoe.AI)
                    elif tictactoe.is_board_full(st.session_state.board):
                        st.session_state.game_over = True
                        streamlit_ui.display_game_over(None)
                    else:
                        st.session_state.ai_turn = False  # Switch back to Player's turn
                        st.rerun()

        # Display the board after each turn
        streamlit_ui.display_board(st.session_state.board)
    else:
        # Display game over message
        pass # The game over message is already displayed by the winner/draw check


if __name__ == "__main__":
    main()