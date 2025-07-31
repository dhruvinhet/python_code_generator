# npc.py
import numpy as np

class NPC:
    """Represents a non-playable character in the simulation."""

    def __init__(self, x, y, map_size):
        """Initializes an NPC object.

        Args:
            x (int): Initial x-coordinate.
            y (int): Initial y-coordinate.
            map_size (int): The size of the map.
        """
        self.x = x
        self.y = y
        self.speed = 1  # Movement speed (units per step)
        self.task = None  # Current task (e.g., move to a location)
        self.map_size = map_size

    def move(self, map_data):
        """Updates the NPC's position based on its assigned task.

        Args:
            map_data (numpy.ndarray): The map environment represented as a 2D array.
        """
        # Simple random movement for now (can be expanded later)
        dx = np.random.randint(-1, 2)
        dy = np.random.randint(-1, 2)

        new_x = self.x + dx
        new_y = self.y + dy

        # Check boundaries and obstacle avoidance
        if 0 <= new_x < self.map_size and 0 <= new_y < self.map_size:
            if map_data[new_y, new_x] == 0:
                self.x = new_x
                self.y = new_y
