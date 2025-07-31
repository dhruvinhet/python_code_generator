# environment.py
import numpy as np


class Environment:
    """Defines the environment in which the NPCs exist."""

    def __init__(self, width, height):
        """Initializes the environment with a width and height.

        Args:
            width (int): The width of the environment.
            height (int): The height of the environment.
        """
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width))

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
        # This function would need to be implemented with a list of NPCs in the environment
        # or a spatial data structure for efficiency.
        return []  # Placeholder implementation