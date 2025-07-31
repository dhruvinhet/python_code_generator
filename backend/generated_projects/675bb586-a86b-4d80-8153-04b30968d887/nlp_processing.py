# nlp_processing.py
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag


def parse_input_text(text):
    """Parses the input text into sentences.

    Args:
        text (str): The input text.

    Returns:
        list: A list of sentences.
    """
    try:
        sentences = sent_tokenize(text)
        return sentences
    except Exception as e:
        print(f"Error parsing text: {e}")
        return []


def extract_actions_and_conditions(sentences):
    """Extracts actions and conditions from the sentences.

    Args:
        sentences (list): A list of sentences.

    Returns:
        tuple: A tuple containing lists of actions and conditions.
    """
    actions = []
    conditions = []
    for sentence in sentences:
        try:
            tokens = word_tokenize(sentence)
            tagged_tokens = pos_tag(tokens)

            # Simple logic to identify actions (verbs) and conditions (nouns/adjectives)
            # Adjust this logic based on the complexity of your NLP requirements
            verbs = [word for word, pos in tagged_tokens if pos.startswith('VB')]  # Verbs (actions)
            nouns_adj = [word for word, pos in tagged_tokens if pos.startswith('NN') or pos.startswith('JJ')] # Nouns/Adjectives (conditions)

            actions.extend(verbs)
            conditions.extend(nouns_adj)
        except Exception as e:
            print(f"Error processing sentence: {e}")

    return actions, conditions


def create_flowchart_data(actions, conditions):
    """Creates flowchart data from actions and conditions.

    Args:
        actions (list): A list of actions.
        conditions (list): A list of conditions.

    Returns:
        dict: A dictionary representing the flowchart data.
    """
    data = {
        "start": {
            "label": "Start",
            "type": "start"
        },
        "end": {
            "label": "End",
            "type": "end"
        },
        "actions": [{
            "label": action,
            "type": "action"
        } for action in actions],
        "conditions": [{
            "label": condition,
            "type": "condition"
        } for condition in conditions]
    }
    return data