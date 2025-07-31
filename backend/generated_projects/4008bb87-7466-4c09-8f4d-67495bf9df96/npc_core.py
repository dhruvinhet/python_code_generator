# npc_core.py
import numpy as np
import random


class NPC:
    """Represents a non-playable character (NPC) in the simulation."""

    def __init__(self, name, traits, env_width, env_height):
        """Initializes an NPC with a name and traits.

        Args:
            name (str): The name of the NPC.
            traits (dict): A dictionary of traits, such as aggression and intelligence.
        """
        self.name = name
        self.traits = traits
        self.x = random.randint(0, env_width - 1)  # Initial x position
        self.y = random.randint(0, env_height - 1)  # Initial y position

    def update(self, environment):
        """Updates the NPC's state based on the environment.

        Args:
            environment (Environment): The environment the NPC is in.
        """
        # Simple random movement
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.x = max(0, min(self.x + dx, environment.width - 1))
        self.y = max(0, min(self.y + dy, environment.height - 1))

        # Interact with the environment
        environment.interact(self)


class Environment:
    """Represents the environment in which the NPCs exist."""

    def __init__(self, width, height):
        """Initializes the environment with a width and height.

        Args:
            width (int): The width of the environment.
            height (int): The height of the environment.
        """
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width))
        self.npcs = []  # Keep track of NPCs in the environment

    def update(self):
        """Updates the environment's state."""
        # Placeholder for environment updates
        pass

    def get_nearby_npcs(self, npc, radius):
        """Gets a list of NPCs within a certain radius of a given NPC.

        Args:
            npc (NPC): The NPC to search around.
            radius (int): The radius to search within.

        Returns:
            list: A list of nearby NPCs.
        """
        nearby_npcs = []
        for other_npc in self.npcs:
            if other_npc != npc:
                distance = np.sqrt((npc.x - other_npc.x)**2 + (npc.y - other_npc.y)**2)
                if distance <= radius:
                    nearby_npcs.append(other_npc)
        return nearby_npcs

    def interact(self, npc):
        """Handles interactions between the NPC and the environment.

        Args:
            npc (NPC): The NPC interacting with the environment.
        """
        # Placeholder for environment interactions (e.g., resource gathering)
        pass


def simulate(npcs, environment, steps):
    """Simulates the interactions of NPCs within an environment over a number of steps.

    Args:
        npcs (list): A list of NPC objects.
        environment (Environment): The environment object.
        steps (int): The number of simulation steps to run.

    Returns:
        list: A list of dictionaries containing simulation data for each step.
    """
    simulation_data = []
    environment.npcs = npcs  # Register npcs to the environment
    for step in range(steps):
        environment.update()
        for npc in npcs:
            npc.update(environment)
        # Record simulation data (example: NPC positions)
        step_data = {
            "step": step,
            "npc_positions": [(npc.x, npc.y) for npc in npcs]
        }
        simulation_data.append(step_data)
    return simulation_data