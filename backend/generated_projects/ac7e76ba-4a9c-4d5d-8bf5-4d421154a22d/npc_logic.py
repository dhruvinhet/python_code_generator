# npc_logic.py
import random
import datetime
import npc_data


def create_npc():
    """Creates a new NPC with random characteristics and initial state."""
    name = npc_data.get_random_name()
    stats = npc_data.get_initial_stats()
    return {
        "name": name,
        "stats": stats,
        "inventory": [],
        "location": "Town Square",
        "day": 0
    }


def simulate_npc_day(npc, day):
    """Simulates a day in the life of an NPC."""
    # Make a copy to avoid modifying the original
    npc = npc.copy()
    npc['day'] = day

    # Determine the action for the day
    action = determine_action(npc)

    # Update the NPC's state based on the action
    update_npc_state(npc, action)

    # Interact with another NPC (optional)
    if random.random() < 0.3:
        try:
            other_npc = create_npc()
            interaction_result = interact(npc, other_npc)
            npc['interaction'] = interaction_result
        except Exception as e:
            npc['interaction'] = f"Interaction failed: {e}"
    else:
        npc['interaction'] = "No interaction"

    # Prepare the data for output
    daily_data = {
        "day": npc['day'],
        "npc_name": npc['name'],
        "action": action,
        "location": npc['location'],
        "interaction": npc['interaction']
    }

    return daily_data


def determine_action(npc):
    """Determines the action the NPC will take based on its state."""
    possible_actions = npc_data.get_possible_actions()
    # Simple random selection for now; could be more sophisticated
    return random.choice(possible_actions)


def interact(npc1, npc2):
    """Simulates an interaction between two NPCs."""
    # Simple interaction logic for now
    interaction_types = ["greeting", "trade", "argument"]
    interaction_type = random.choice(interaction_types)

    if interaction_type == "greeting":
        return f"{npc1['name']} greets {npc2['name']}."
    elif interaction_type == "trade":
        return f"{npc1['name']} trades with {npc2['name']}."
    elif interaction_type == "argument":
        return f"{npc1['name']} argues with {npc2['name']}."
    else:
        return "Interaction error."


def update_npc_state(npc, action):
    """Updates the NPC's state based on the action taken."""
    if action == "Forage for food":
        npc['inventory'].append("Food")
    elif action == "Go to the market":
        npc['location'] = "Market"
    elif action == "Rest":
        # Recover some stats (simplified)
        for stat in npc['stats']:
            if isinstance(npc['stats'][stat], (int, float)): #Check to see if its a number
                npc['stats'][stat] += 1
    elif action == "Explore the forest":
        npc['location'] = "Forest"
    else:
        pass  # No state change for other actions