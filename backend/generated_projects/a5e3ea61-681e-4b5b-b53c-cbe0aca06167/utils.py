# utils.py
import random

WORD_LIST = []


def load_word_list(filepath="words.txt"):
    """Loads a list of words from a file.  If file not found, creates basic word list."""
    global WORD_LIST
    try:
        with open(filepath, 'r') as file:
            WORD_LIST = [word.strip() for word in file.readlines()]  # strip newline characters
    except FileNotFoundError:
        WORD_LIST = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog"]  # Basic word list if none available
    except Exception as e:
        print(f"Error loading word list: {e}")
        WORD_LIST = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog"]  # Ensure list is not empty

    return WORD_LIST


def generate_random_words(num_words):
    """Generates a string of random words from the word list."""
    global WORD_LIST
    if not WORD_LIST:
        WORD_LIST = load_word_list()  # Load word list if empty

    if not WORD_LIST:
        return "Error: Word list is empty. Ensure words.txt is present or create a default list within utils.py"  # Handle completely empty list

    return ' '.join(random.choice(WORD_LIST) for _ in range(num_words))


# Load Word List (only if this file is run as main)
if __name__ == '__main__':
    words = load_word_list()
    if words:
        print(f"Loaded {len(words)} words.")
    else:
        print("Failed to load words.")
