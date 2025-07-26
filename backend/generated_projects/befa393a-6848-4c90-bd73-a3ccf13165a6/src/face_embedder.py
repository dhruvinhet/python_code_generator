# src/face_embedder.py
import tensorflow as tf
from tensorflow import keras
import numpy as np
import cv2


def extract_embeddings(image, face_boxes, model_path):
    """Extracts facial embeddings from detected faces using a pre-trained model.

    Args:
        image (numpy.ndarray): The input image.
        face_boxes (list): A list of face bounding boxes (x, y, width, height).
        model_path (str): Path to the pre-trained face embedding model (.h5 file).

    Returns:
        numpy.ndarray: A numpy array containing the facial embeddings for each detected face.
    """
    try:
        # Load the pre-trained face embedding model
        model = keras.models.load_model(model_path)

        embeddings = []
        for box in face_boxes:
            x, y, w, h = box
            face = image[y:y+h, x:x+w]
            face = cv2.resize(face, (160, 160))  # Standard FaceNet input size
            face = face.astype('float32')
            mean, std = face.mean(), face.std()
            face = (face - mean) / std  # Normalize the face
            face = np.expand_dims(face, axis=0)
            try:
                embedding = model.predict(face)[0]
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error during prediction: {e}")
                continue #skip this face

        return np.array(embeddings)

    except Exception as e:
        print(f"Error in embedding extraction: {e}")
        return np.array([])
