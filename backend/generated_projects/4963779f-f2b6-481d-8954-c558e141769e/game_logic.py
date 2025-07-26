# game_logic.py
import random


def get_weighted_computer_choice(weight_rock, weight_paper, weight_scissors):
    """Gets the computer's choice with weighted probabilities."""
    choices = ['rock', 'paper', 'scissors']
    weights = [weight_rock, weight_paper, weight_scissors]

    # Normalize weights to ensure they sum to 1.
    total_weight = sum(weights)
    if total_weight <= 0:
      raise ValueError("Weights must sum to a value greater than zero.")
    
    normalized_weights = [w / total_weight for w in weights]
    
    # Handle potential rounding errors which cause sum to be slightly off
    weight_sum = sum(normalized_weights)
    if abs(weight_sum - 1.0) > 1e-9:  # Using a small tolerance for floating-point comparison
      difference = 1.0 - weight_sum
      # Add the difference to the first weight
      normalized_weights[0] += difference


    try:
        return random.choices(choices, weights=normalized_weights, k=1)[0]
    except ValueError as e:
        raise ValueError(f"Invalid weights. Weights must be non-negative. {e}") from e
    except IndexError as e:
        raise IndexError(f"Error during choice selection: {e}") from e