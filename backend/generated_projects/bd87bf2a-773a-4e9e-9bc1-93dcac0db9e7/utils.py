# utils.py
import cv2
import numpy as np
import json

# Load configuration from a JSON file
def load_config(config_file):
    """Loads configuration settings from a JSON file.

    Args:
        config_file (str): The path to the JSON configuration file.

    Returns:
        dict: A dictionary containing the configuration settings.
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{config_file}'.")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

# Resize an image
def resize_image(image, width=None, height=None, inter=cv2.INTER_AREA):
    """Resizes an image to the specified width and/or height.

    Args:
        image (numpy.ndarray): The input image.
        width (int, optional): The desired width of the resized image. Defaults to None.
        height (int, optional): The desired height of the resized image. Defaults to None.
        inter (int, optional): The interpolation method to use for resizing. Defaults to cv2.INTER_AREA.

    Returns:
        numpy.ndarray: The resized image.
    """
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    try:
        resized = cv2.resize(image, dim, interpolation=inter)
        return resized
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image

# Convert BGR image to RGB
def bgr_to_rgb(image):
    """Converts a BGR image to RGB.

    Args:
        image (numpy.ndarray): The input BGR image.

    Returns:
        numpy.ndarray: The converted RGB image.
    """
    try:
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"Error converting BGR to RGB: {e}")
        return image


if __name__ == '__main__':
    # Example Usage:
    # Create a dummy image
    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)

    # Resize the image to a width of 320 pixels
    resized_image = resize_image(dummy_image, width=320)

    # Convert the resized image to RGB
    rgb_image = bgr_to_rgb(resized_image)

    #Load configurations:
    config = load_config("config.json") # replace with your config file name/path if different

    print("Resized Image Shape:", resized_image.shape)
    print("RGB Image Shape:", rgb_image.shape)
    print("Loaded Configs", config)
