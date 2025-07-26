# main.py
import argparse
import os
import cv2
import tensorflow as tf
from src import face_detector
from src import face_embedder
from src import adversarial_defense
from src import utils
import numpy as np


def main():
    """Entry point for the application. Handles argument parsing, model loading, and execution of face recognition pipeline."""
    parser = argparse.ArgumentParser(description="Adversarial Face Recognition Framework")
    parser.add_argument("--image_path", type=str, required=True, help="Path to the input image.")
    parser.add_argument("--detection_model_path", type=str, default="models/face_detection/detector.pb", help="Path to the face detection model.")
    parser.add_argument("--embedding_model_path", type=str, default="models/face_embedding/embedding_model.h5", help="Path to the face embedding model.")
    parser.add_argument("--adversarial", action='store_true', help="Enable adversarial defense.")
    args = parser.parse_args()

    # Load the image
    try:
        image = utils.load_image(args.image_path)
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Detect faces
    try:
        face_boxes, confidence = face_detector.detect_faces(image, args.detection_model_path)
        if not face_boxes:
            print("No faces detected.")
            return
    except Exception as e:
        print(f"Error detecting faces: {e}")
        return

    # Extract embeddings
    try:
        face_embeddings = face_embedder.extract_embeddings(image, face_boxes, args.embedding_model_path)
    except Exception as e:
        print(f"Error extracting embeddings: {e}")
        return

    # Apply adversarial defense if enabled
    if args.adversarial:
        try:
            adversarial_image = adversarial_defense.apply_adversarial_training(image, face_embeddings)
            #Replace original image with adversarial image
            if adversarial_image is not None:
                image = adversarial_image
            else:
                print("Adversarial defense failed, using original image.")

        except Exception as e:
            print(f"Error applying adversarial defense: {e}")
            return
        try:
             face_boxes, confidence = face_detector.detect_faces(image, args.detection_model_path)
             face_embeddings = face_embedder.extract_embeddings(image, face_boxes, args.embedding_model_path)

        except Exception as e:
            print(f"Error re detecting/embedding after adversarial defense: {e}")
            return


    # Perform face recognition (Placeholder - replace with actual recognition logic)
    print("Detected Faces & Embeddings (Placeholder - Add Recognition Logic):")
    for i, (box, embedding) in enumerate(zip(face_boxes, face_embeddings)):
        print(f"Face {i+1}: Box={box}, Embedding Shape={embedding.shape}")

        # Draw bounding boxes on the image
        x, y, w, h = box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Save or display the output image
    output_path = "output.jpg"
    try:
        utils.save_image(image, output_path)
        print(f"Output image saved to {output_path}")

    except Exception as e:
        print(f"Error saving image: {e}")
        return


if __name__ == "__main__":
    main()
