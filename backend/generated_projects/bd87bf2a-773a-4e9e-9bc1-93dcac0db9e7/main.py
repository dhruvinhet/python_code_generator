# main.py
import streamlit as st
import crime_detector
import video_stream
import report_generator
import utils
import cv2
import time
import os

# Load configuration (assuming config.json exists and contains necessary paths)
try:
    config = utils.load_config("config.json")
    model_path = config.get("model_path")
    frame_width = config.get("frame_width", 640)  # default to 640 if not in config
    class_names = config.get("class_names", ["person", "knife", "gun", "fight"])
    report_frequency = config.get("report_frequency", 60)
except Exception as e:
    st.error(f"Error loading configuration: {e}")
    st.stop()


def main():
    st.title("CrimsonWatch: Real-time Crime Monitoring")

    # Sidebar for settings
    st.sidebar.header("Settings")
    video_source = st.sidebar.selectbox("Video Source", options=["Camera", "Video File"])

    if video_source == "Camera":
        source = 0  # Default camera
    else:
        source = st.sidebar.text_input("Video File Path", "sample_video.mp4") # default file, can be customized by user

    confidence_threshold = st.sidebar.slider("Confidence Threshold", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

    # Load the crime detection model
    try:
        model = crime_detector.load_model(model_path)
        if model is None:
            st.error("Failed to load the crime detection model.")
            st.stop()
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.stop()

    # Initialize video stream
    try:
        video = video_stream.VideoStream(src=source).start()
        time.sleep(2.0)  # Allow camera to warm up
    except Exception as e:
        st.error(f"Error initializing video stream: {e}")
        st.stop()

    # Streamlit image placeholder
    image_placeholder = st.empty()

    frame_count = 0 # Count of frames processed

    while True:
        try:
            frame = video.read()
            if frame is None:
                st.write("End of video stream.")
                break

            frame_count += 1

            # Preprocess the frame
            resized_frame = utils.resize_image(frame, width=frame_width)
            rgb_frame = utils.bgr_to_rgb(resized_frame)

            # Detect crimes in the frame
            detections = crime_detector.detect_crimes(model, rgb_frame, confidence_threshold)

            # Draw bounding boxes and labels on the frame
            for *box, confidence, class_id in detections:
                label = class_names[int(class_id)]
                confidence = round(confidence, 2)
                label_text = f"{label}: {confidence}"

                #Scale box to original frame size
                ih, iw, _ = frame.shape
                x1 = int(box[0] * iw / frame_width)
                y1 = int(box[1] * ih / frame_width)
                x2 = int(box[2] * iw / frame_width)
                y2 = int(box[3] * ih / frame_width)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Generate report and save video snippet
                if frame_count % report_frequency == 0: # generate report every n frames
                  report_generator.generate_report(label, confidence)
                  report_generator.save_video_snippet(frame, label)
                  report_generator.store_event_data(label, confidence)

            # Update the Streamlit image placeholder with the processed frame
            image_placeholder.image(frame, channels="BGR", use_column_width=True)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            st.error(f"Error processing frame: {e}")
            break # Ensure loop breaks on error

    # Stop the video stream
    try:
        video.stop()
        cv2.destroyAllWindows()
    except Exception as e:
        st.error(f"Error during shutdown: {e}")

# Run the main function if the script is executed
if __name__ == "__main__":
    main()
