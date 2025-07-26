# video_stream.py
import cv2
from threading import Thread

# Class for handling video stream
class VideoStream:
    """A class that encapsulates video stream acquisition from various sources.

    This class uses multi-threading to continuously read frames from a video source
    (camera, video file, or RTSP stream) in a separate thread, ensuring that the
    main thread is not blocked by I/O operations.
    """

    def __init__(self, src=0):
        """Initializes the VideoStream object.

        Args:
            src (int or str): The source of the video stream. If an integer, it
                              represents the camera index. If a string, it represents
                              the path to a video file or an RTSP stream URL.
        """
        try:
            self.stream = cv2.VideoCapture(src)
            if not self.stream.isOpened():
                raise IOError("Cannot open video source")
            self.stopped = False
            (self.grabbed, self.frame) = self.stream.read()
        except Exception as e:
            print(f"Error initializing video stream: {e}")
            self.stopped = True
            self.frame = None

    def start(self):
        """Starts the video stream acquisition thread.

        Returns:
            self: Returns the VideoStream object itself, allowing for method chaining.
        """
        if not self.stopped:
            Thread(target=self.update, args=()).start()
        return self

    def update(self):
        """Continuously reads frames from the video stream and updates the
        internal frame buffer.
        """
        while not self.stopped:
            try:
                (self.grabbed, self.frame) = self.stream.read()
                if not self.grabbed:
                    self.stop()
                    break
            except Exception as e:
                print(f"Error reading frame: {e}")
                self.stop()
                break

    def read(self):
        """Returns the most recently read frame from the video stream.

        Returns:
            numpy.ndarray: The most recently read frame, or None if the stream has
                           been stopped.
        """
        return self.frame

    def stop(self):
        """Stops the video stream acquisition thread and releases the video
        capture object.
        """
        self.stopped = True
        try:
            self.stream.release()
        except Exception as e:
            print(f"Error releasing video stream: {e}")

    def get_frame(self):
        """Gets the current frame from the video stream.

        Returns:
            numpy.ndarray: The current frame.
        """
        return self.frame


if __name__ == '__main__':
    # Example usage: Capture video from the default camera
    video_stream = VideoStream(src=0).start()
    try:
        while True:
            frame = video_stream.read()
            if frame is None:
                break
            cv2.imshow('Video Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        video_stream.stop()
        cv2.destroyAllWindows()
