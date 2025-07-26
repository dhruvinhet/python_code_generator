# report_generator.py
import datetime
import cv2
import pandas as pd
import os

REPORT_DIR = "reports"
VIDEO_SNIPPETS_DIR = "video_snippets"
EVENT_DATA_FILE = "event_data.csv"

# Ensure directories exist
try:
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(VIDEO_SNIPPETS_DIR, exist_ok=True)
except Exception as e:
    print(f"Error creating directories: {e}")

# Function to generate a report of detected crimes
def generate_report(crime_type, confidence):
    """Generates a report of a detected crime, including timestamp and crime details.

    Args:
        crime_type (str): The type of crime detected.
        confidence (float): The confidence score of the detection.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = os.path.join(REPORT_DIR, f"crime_report_{timestamp}.txt")

    try:
        with open(report_file, "w") as f:
            f.write(f"Crime Detected: {crime_type}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Confidence: {confidence:.2f}\n")
        print(f"Report generated: {report_file}")
    except Exception as e:
        print(f"Error generating report: {e}")

# Function to save a video snippet of the detected crime
def save_video_snippet(frame, crime_type, frame_rate=30.0, duration=5, fourcc = cv2.VideoWriter_fourcc(*'mp4v')):
    """Saves a short video snippet of the detected crime.

    Args:
        frame (numpy.ndarray): The frame containing the detected crime.
        crime_type (str): The type of crime detected.
        frame_rate (float): The frame rate for the video snippet.
        duration (int): The duration of the video snippet in seconds.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(VIDEO_SNIPPETS_DIR, f"crime_snippet_{crime_type}_{timestamp}.mp4")

    try:
        height, width, _ = frame.shape
        writer = cv2.VideoWriter(output_file, fourcc, frame_rate, (width, height))

        # Write frames for the specified duration
        if frame is not None:
            for _ in range(duration * int(frame_rate)):
                writer.write(frame)

        writer.release()
        print(f"Video snippet saved: {output_file}")
    except Exception as e:
        print(f"Error saving video snippet: {e}")


# Function to store event data to a CSV file
def store_event_data(crime_type, confidence):
    """Stores event data (crime type, timestamp, confidence) to a CSV file.

    Args:
        crime_type (str): The type of crime detected.
        confidence (float): The confidence score of the detection.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    event_data = {"timestamp": [timestamp], "crime_type": [crime_type], "confidence": [confidence]}
    df = pd.DataFrame(event_data)

    try:
        if os.path.exists(EVENT_DATA_FILE):
            # Append to existing CSV
            df.to_csv(EVENT_DATA_FILE, mode='a', header=False, index=False)
        else:
            # Create new CSV
            df.to_csv(EVENT_DATA_FILE, header=True, index=False)
        print(f"Event data stored in: {EVENT_DATA_FILE}")
    except Exception as e:
        print(f"Error storing event data: {e}")

if __name__ == '__main__':
    # Example usage
    generate_report("Theft", 0.85)
    # Create a dummy frame (replace with your actual frame)
    dummy_frame = cv2.imread('test_image.jpg')  # Provide a sample image
    if dummy_frame is None:
        dummy_frame = cv2.imread("utils/test_image.jpg") # Check utils directory for test image
        if dummy_frame is None: # If image STILL not found
            dummy_frame =  cv2.imread("../utils/test_image.jpg") # check one level up
            if dummy_frame is None:
                dummy_frame =  cv2.imread("../../utils/test_image.jpg") # check two levels up
                if dummy_frame is None:
                     dummy_frame = cv2.imread("../../../utils/test_image.jpg") # check three levels up
        if dummy_frame is None:
            print("Warning: Could not find test_image.jpg.  Snippet saving may fail.")
    #dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8) # alternative if no test image present
    save_video_snippet(dummy_frame, "Theft")
    store_event_data("Theft", 0.85)
