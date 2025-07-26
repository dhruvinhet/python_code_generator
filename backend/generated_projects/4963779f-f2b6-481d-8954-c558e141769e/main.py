# main.py
import random
from game_logic import get_weighted_computer_choice


def get_player_choice():
    """Gets the player's choice from user input."""
    while True:
        choice = input("Choose rock, paper, or scissors: ").lower()
        if choice in ['rock', 'paper', 'scissors']:
            return choice
        else:
            print("Invalid choice. Please try again.")


def determine_winner(player_choice, computer_choice):
    """Determines the winner of the game."""
    print(f"You chose: {player_choice}")
    print(f"Computer chose: {computer_choice}")

    if player_choice == computer_choice:
        return "It's a tie!"
    elif (player_choice == 'rock' and computer_choice == 'scissors') or \
            (player_choice == 'paper' and computer_choice == 'rock') or \
            (player_choice == 'scissors' and computer_choice == 'paper'):
        return "You win!"
    else:
        return "You lose!"


def play_game():
    """Plays a single round of Rock, Paper, Scissors."""
    player_choice = get_player_choice()
    try:
        computer_choice = get_weighted_computer_choice(0.4, 0.3, 0.3)  # Adjust weights as needed.
    except ValueError as e:
        print(f"Error: {e}.  Using random choice instead.")
        computer_choice = random.choice(['rock', 'paper', 'scissors'])
    result = determine_winner(player_choice, computer_choice)
    print(result)


if __name__ == "__main__":
    """Main entry point of the game.  Handles game loop."""
    while True:
        play_game()
        play_again = input("Play again? (y/n): ").lower()
        if play_again != 'y':
            break
    print("Thanks for playing!")