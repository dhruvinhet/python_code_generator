# game_logic.py
import random


def create_board(rows, cols, num_bombs):
    """Creates a minesweeper board with specified dimensions and number of bombs."""
    if num_bombs >= rows * cols:
        raise ValueError("Number of bombs cannot exceed the number of tiles.")

    board = [[0 for _ in range(cols)] for _ in range(rows)]
    bombs_placed = 0
    while bombs_placed < num_bombs:
        row = random.randint(0, rows - 1)
        col = random.randint(0, cols - 1)
        if board[row][col] != -1:
            board[row][col] = -1  # -1 represents a bomb
            bombs_placed += 1
    return board


def reveal_tile(board, revealed, row, col):
    """Reveals a tile on the board and returns the result (diamond, bomb, or already revealed)."""
    if revealed[row][col]:
        return "already revealed"

    if board[row][col] == -1:
        return "bomb"
    else:
        revealed[row][col] = True
        return "diamond"


def calculate_multiplier(revealed, board):
    """Calculates the winnings multiplier based on the number of revealed diamonds."""
    revealed_diamonds = 0
    total_tiles = len(board) * len(board[0])

    for i in range(len(board)):
        for j in range(len(board[0])):
            if revealed[i][j] and board[i][j] != -1:
                revealed_diamonds += 1

    bombs = sum(row.count(-1) for row in board)
    safe_tiles = total_tiles - bombs

    if revealed_diamonds == 0:
        return 1.0

    if safe_tiles == 0:
        return 1.0

    remaining_safe_tiles = safe_tiles - revealed_diamonds
    if remaining_safe_tiles <= 0:
        return 1.0

    return (safe_tiles / remaining_safe_tiles)  # More balanced


def is_game_over(board, revealed):
    """Checks if the game is over (a bomb has been revealed)."""
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == -1 and revealed[i][j]:
                return True
    return False


def is_board_complete(board, revealed):
  """Checks if the board is complete (only bombs are left hidden)."""
  for i in range(len(board)):
    for j in range(len(board[0])):
      if board[i][j] != -1 and not revealed[i][j]:
        return False
  return True
