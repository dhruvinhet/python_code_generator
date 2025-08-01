import random

def get_all_questions():
    """
    Returns a list of dictionaries, each representing an MCQ question.
    Each dictionary contains 'question', 'options' (a list of strings),
    and 'answer' (the correct option string).
    This data can be extended or loaded from an external file (e.g., JSON, CSV).
    """
    questions = [
        {
            "question": "What is the capital of France?",
            "options": ["Berlin", "Madrid", "Paris", "Rome"],
            "answer": "Paris"
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["Earth", "Mars", "Jupiter", "Venus"],
            "answer": "Mars"
        },
        {
            "question": "What is the largest ocean on Earth?",
            "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
            "answer": "Pacific Ocean"
        },
        {
            "question": "Who wrote 'Romeo and Juliet'?",
            "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
            "answer": "William Shakespeare"
        },
        {
            "question": "What is the chemical symbol for water?",
            "options": ["O2", "H2O", "CO2", "NACL"],
            "answer": "H2O"
        },
        {
            "question": "What is the largest desert in the world?",
            "options": ["Gobi Desert", "Sahara Desert", "Arabian Desert", "Antarctic Polar Desert"],
            "answer": "Antarctic Polar Desert"
        },
        {
            "question": "Which country is known as the Land of the Rising Sun?",
            "options": ["China", "South Korea", "Japan", "Thailand"],
            "answer": "Japan"
        },
        {
            "question": "What is the smallest prime number?",
            "options": ["0", "1", "2", "3"],
            "answer": "2"
        }
    ]
    # Optionally shuffle the order of questions to provide a fresh experience on restart
    random.shuffle(questions)
    return questions
