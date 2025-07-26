# text_generator.py
import random

# Function to generate a random string of words
def generate_text(num_words=100):
    """Generates a random string of words.

    Args:
        num_words (int): The number of words to generate.

    Returns:
        str: A string of random words.
    """
    word_list = ["the", "a", "an", "is", "are", "was", "were", "be", "being", "been", "to", "from", "of", "and", "or", "but", "not", "in", "on", "at", "by", "for", "with", "about", "against", "between", "through", "during", "before", "after", "above", "below", "up", "down", "out", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "one", "two", "three", "four", "five", "first", "second", "last", "own", "same", "so", "than", "too", "very", "can", "could", "will", "would", "shall", "should", "may", "might", "must"]

    text = ' '.join(random.choice(word_list) for _ in range(num_words))
    return text


if __name__ == '__main__':
    # Example Usage (optional, for testing)
    random_text = generate_text(50)
    print(random_text)