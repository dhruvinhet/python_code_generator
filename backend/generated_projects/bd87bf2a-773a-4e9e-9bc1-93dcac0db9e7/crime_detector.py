# crime_detector.py
import tensorflow as tf
import cv2
import numpy as np

# Load the deep learning model
def load_model(model_path):
    """Loads the TensorFlow/Keras model from the specified path.

    Args:
        model_path (str): The path to the .h5 model file.

    Returns:
        tf.keras.Model: The loaded deep learning model.
    """
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"Model loaded successfully from {model_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Preprocess the frame for the model
def preprocess_frame(frame, target_size=(640, 480)):
    """Preprocesses the input frame for the deep learning model.

    Args:
        frame (numpy.ndarray): The input frame (image).
        target_size (tuple): The target size (width, height) for resizing the frame.

    Returns:
        numpy.ndarray: The preprocessed frame.
    """
    try:
        resized_frame = cv2.resize(frame, target_size)
        img_array = tf.keras.utils.img_to_array(resized_frame)
        expanded_img_array = np.expand_dims(img_array, axis=0)
        preprocessed_img = tf.keras.applications.mobilenet.preprocess_input(expanded_img_array) # Using MobileNet preprocessing as an example

        return preprocessed_img
    except Exception as e:
        print(f"Error preprocessing frame: {e}")
        return None


# Detect crimes in a video frame
def detect_crimes(model, frame, confidence_threshold=0.5):
    """Detects crimes in a given video frame using the loaded deep learning model.

    Args:
        model (tf.keras.Model): The loaded deep learning model.
        frame (numpy.ndarray): The input frame (image).
        confidence_threshold (float): The minimum confidence score for a detection to be considered valid.

    Returns:
        list: A list of detections, where each detection is a list containing the bounding box coordinates, confidence score, and class ID.
    """

    try:
        img = cv2.resize(frame, (640, 480))
        img = np.expand_dims(img, 0)
        results = model.predict(img, verbose=0)
        detections = []

        for result in results:
            for *box, confidence, class_id in result:
                if confidence > confidence_threshold:
                    detections.append([box[0], box[1], box[2], box[3], confidence, int(class_id)])

        return detections

    except Exception as e:
        print(f"Error during crime detection: {e}")
        return []


if __name__ == '__main__':
    # Example usage (replace with your actual model path and test image)
    model_path = 'model/crime_detection_model.h5'
    model = load_model(model_path)

    if model:
        # Create a dummy frame for testing
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Detect crimes in the dummy frame
        detections = detect_crimes(model, dummy_frame)

        print("Detections:", detections)
