# src/face_detector.py
import cv2
import numpy as np


def detect_faces(image, model_path):
    """Detects faces in an image using a pre-trained model.

    Args:
        image (numpy.ndarray): The input image.
        model_path (str): Path to the pre-trained face detection model (e.g., .pb file).

    Returns:
        tuple: A tuple containing a list of face bounding boxes (x, y, width, height) and confidence scores.
    """
    try:
        # Load the pre-trained face detection model
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') # using Haar cascade for simplicity; consider DNN for better accuracy
        if face_cascade.empty():
            raise IOError('Unable to load face cascade classifier xml file')

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces using the cascade classifier
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        face_boxes = []
        confidence_scores = []

        for (x, y, w, h) in faces:
            face_boxes.append((x, y, w, h))
            confidence_scores.append(1.0)  # Placeholder: Haar cascades don't directly provide confidence scores, assign 1.0 for demonstration

        return face_boxes, confidence_scores

    except Exception as e:
        print(f"Error in face detection: {e}")
        return [], []
