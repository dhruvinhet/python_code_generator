# main.py
import random

# Constants for choices
ROCK = 'rock'
PAPER = 'paper'
SCISSORS = 'scissors'


def get_player_choice():
    """Gets the player's choice (rock, paper, or scissors) from user input.

    Handles invalid input and ensures the choice is valid.
    """
    while True:
        choice = input("Choose rock, paper, or scissors: ").lower()
        if choice in [ROCK, PAPER, SCISSORS]:
            return choice
        else:
            print("Invalid choice. Please try again.")


def get_ai_choice():
    """Generates a random choice (rock, paper, or scissors) for the AI.

    Returns:
        str: The AI's choice.
    """
    return random.choice([ROCK, PAPER, SCISSORS])


def determine_winner(player_choice, ai_choice):
    """Determines the winner of the round based on player and AI choices.

    Args:
        player_choice (str): The player's choice.
        ai_choice (str): The AI's choice.

    Returns:
        str: A message indicating the result of the round.
    """
    print(f"You chose {player_choice}, AI chose {ai_choice}.")

    if player_choice == ai_choice:
        return "It's a tie!"
    elif (player_choice == ROCK and ai_choice == SCISSORS) or \
         (player_choice == PAPER and ai_choice == ROCK) or \
         (player_choice == SCISSORS and ai_choice == PAPER):
        return "You win!"
    else:
        return "AI wins!"


def play_round():
    """Plays a single round of Rock, Paper, Scissors.

    Gets player and AI choices, determines the winner, and prints the result.
    """
    player_choice = get_player_choice()
    ai_choice = get_ai_choice()
    result = determine_winner(player_choice, ai_choice)
    print(result)


def main():
    """Main function to run the Rock, Paper, Scissors game.

    Allows the player to play multiple rounds until they choose to quit.
    """
    print("Welcome to Rock, Paper, Scissors!")

    while True:
        try:
            play_round()
            play_again = input("Play again? (yes/no): ").lower()
            if play_again != 'yes':
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break # Exit the game loop if an unrecoverable error occurs.

    print("Thanks for playing!")


# Entry point for the script
if __name__ == "__main__":
    main()
