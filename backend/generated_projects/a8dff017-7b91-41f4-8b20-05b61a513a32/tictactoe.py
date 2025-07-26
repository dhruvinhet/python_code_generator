# tictactoe.py
import random

# Define constants for players
PLAYER = 'X'
AI = 'O'


def initialize_board():
    """Initializes an empty Tic-Tac-Toe board."""
    return [' '] * 9


def print_board(board):
    """Prints the Tic-Tac-Toe board in a user-friendly format."""
    print("-------------")
    for i in range(3):
        print(f"| {board[i * 3]} | {board[i * 3 + 1]} | {board[i * 3 + 2]} |")
        print("-------------")


def is_winner(board, player):
    """Checks if the given player has won the game."""
    # Check rows
    for i in range(3):
        if board[i * 3] == board[i * 3 + 1] == board[i * 3 + 2] == player:
            return True
    # Check columns
    for i in range(3):
        if board[i] == board[i + 3] == board[i + 6] == player:
            return True
    # Check diagonals
    if board[0] == board[4] == board[8] == player:
        return True
    if board[2] == board[4] == board[6] == player:
        return True
    return False


def is_board_full(board):
    """Checks if the board is full."""
    return ' ' not in board


def get_available_moves(board):
    """Returns a list of available moves (empty spaces) on the board."""
    return [i for i, space in enumerate(board) if space == ' ']


def minimax(board, depth, maximizing_player):
    """Implements the Minimax algorithm for AI decision-making."""
    if is_winner(board, AI):
        return 10 - depth
    if is_winner(board, PLAYER):
        return depth - 10
    if is_board_full(board):
        return 0

    if maximizing_player:
        max_eval = float('-inf')
        for move in get_available_moves(board):
            board[move] = AI
            eval = minimax(board, depth + 1, False)
            board[move] = ' '  # Undo the move
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_available_moves(board):
            board[move] = PLAYER
            eval = minimax(board, depth + 1, True)
            board[move] = ' '  # Undo the move
            min_eval = min(min_eval, eval)
        return min_eval


def get_ai_move(board):
    """Calculates the best move for the AI using the Minimax algorithm."""
    best_move = None
    best_eval = float('-inf')

    for move in get_available_moves(board):
        board[move] = AI
        eval = minimax(board, 0, False)
        board[move] = ' '  # Undo the move

        if eval > best_eval:
            best_eval = eval
            best_move = move

    return best_move


def make_move(board, move, player):
    """Makes a move on the board for the given player."""
    if 0 <= move < len(board) and board[move] == ' ':
        board[move] = player
    else:
        return False #Indicate that move was not valid
    return True
