# game_logic.py
import random

# Constants for probabilities (making losing more likely)
WIN_PROBABILITY = 0.3  # 30% chance of winning
PAYOUT_MULTIPLIER = 1.5  # Payout is 1.5 times the bet amount

# Function to simulate a round of the gambling game
def play_game(bet_amount):
    """Simulates a round of the gambling game.

    Args:
        bet_amount (float): The amount the player bets.

    Returns:
        tuple: A tuple containing the result ("win" or "lose") and the win amount (if any).
    """
    if not isinstance(bet_amount, (int, float)) or bet_amount <= 0:
        raise ValueError("Bet amount must be a positive number.")

    if random.random() < WIN_PROBABILITY:
        # Player wins
        win_amount = bet_amount * PAYOUT_MULTIPLIER
        return "win", win_amount
    else:
        # Player loses
        return "lose", 0


# Function to calculate win probability
def calculate_win_probability():
    """Calculates the win probability.

    Returns:
        float: The win probability.
    """
    return WIN_PROBABILITY


# Function to update the balance (not used directly, but kept for consistency)
def update_balance(current_balance, bet_amount, result):
    """Updates the current balance based on the game result.

    Args:
        current_balance (float): The player's current balance.
        bet_amount (float): The amount the player bet.
        result (str): The result of the game ("win" or "lose").

    Returns:
        float: The updated balance.
    """
    if result == "win":
        return current_balance + (bet_amount * PAYOUT_MULTIPLIER)
    else:
        return current_balance - bet_amount


# Function to validate the bet amount
def validate_bet(bet_amount, current_balance):
    """Validates that the bet amount is within acceptable limits.

    Args:
        bet_amount (float): The amount the player wants to bet.
        current_balance (float): The player's current balance.

    Returns:
        bool: True if the bet is valid, False otherwise.
    """
    return 0.01 <= bet_amount <= current_balance
