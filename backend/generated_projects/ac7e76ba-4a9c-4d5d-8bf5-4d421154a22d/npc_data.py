# npc_data.py
import random
import datetime


def get_random_name():
    """Generates a random name for an NPC."""
    first_names = ["Alice", "Bob", "Charlie", "David", "Eve"]
    last_names = ["Smith", "Jones", "Williams", "Brown", "Davis"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def get_initial_stats():
    """Generates initial stats for an NPC."""
    return {
        "health": random.randint(50, 100),
        "mana": random.randint(20, 50),
        "stamina": random.randint(70, 100)
    }


def get_possible_actions():
    """Returns a list of possible actions for an NPC."""
    return ["Forage for food", "Go to the market", "Rest", "Explore the forest"]