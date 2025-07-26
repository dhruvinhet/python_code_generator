# src/utils.py
import cv2
import numpy as np


def load_image(image_path):
    """Loads an image from the given path.

    Args:
        image_path (str): The path to the image file.

    Returns:
        numpy.ndarray: The loaded image as a NumPy array.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #convert to RGB
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        raise


def save_image(image, output_path):
    """Saves an image to the specified path.

    Args:
        image (numpy.ndarray): The image to save.
        output_path (str): The path to save the image to.
    """
    try:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) #convert back to BGR for cv2
        cv2.imwrite(output_path, image)
    except Exception as e:
        print(f"Error saving image: {e}")
        raise


def preprocess_image(image, target_size=(160, 160)):
    """Preprocesses the image by resizing and normalizing pixel values.

    Args:
        image (numpy.ndarray): The input image.
        target_size (tuple): The desired size of the image.

    Returns:
        numpy.ndarray: The preprocessed image.
    """
    try:
        image = cv2.resize(image, target_size)
        image = image.astype('float32')
        image /= 255.0  # Normalize pixel values to [0, 1]
        return image
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None
