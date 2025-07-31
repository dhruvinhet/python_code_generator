# map_generator.py
import numpy as np
from PIL import Image


def generate_random_map(size, obstacle_probability=0.2):
    """Generates a map with randomly placed obstacles.

    Args:
        size (int): The size of the map (size x size).
        obstacle_probability (float): Probability of a cell being an obstacle.

    Returns:
        numpy.ndarray: A 2D numpy array representing the map.
                       0: Free space, 1: Obstacle.
    """
    map_data = np.random.choice([0, 1], size=(size, size), p=[1 - obstacle_probability, obstacle_probability])
    return map_data


def load_map_from_image(image_path):
    """Loads a map from an image file.

    Args:
        image_path (str): The path to the image file.

    Returns:
        numpy.ndarray: A 2D numpy array representing the map.
                       Black pixels are considered obstacles (1), others are free space (0).
    """
    try:
        img = Image.open(image_path).convert('L')  # Convert to grayscale
        map_data = np.array(img)
        map_data = np.where(map_data < 128, 1, 0)  # Threshold to create obstacles
        return map_data
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None


def create_grid_map(size):
    """Creates a basic grid-based map with no obstacles.

    Args:
        size (int): The size of the map (size x size).

    Returns:
        numpy.ndarray: A 2D numpy array representing the map (all zeros).
    """
    map_data = np.zeros((size, size), dtype=int)
    return map_data


def is_valid_location(map_data, x, y):
    """Checks if a given location is within the map boundaries and not an obstacle.

    Args:
        map_data (numpy.ndarray): The map environment.
        x (int): The x-coordinate of the location.
        y (int): The y-coordinate of the location.

    Returns:
        bool: True if the location is valid, False otherwise.
    """
    if 0 <= x < map_data.shape[1] and 0 <= y < map_data.shape[0] and map_data[y, x] == 0:
        return True
    else:
        return False