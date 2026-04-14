"""Camera capture module for sensorium.

Provides OpenCV-based video capture from Logitech C920 or compatible USB camera.
Handles frame reading, resizing, and error management.
"""

import cv2
import numpy as np
from typing import Optional


class CameraCapture:
    """Manages video capture from USB camera (C920).

    Captures frames at 30-60 fps and resizes to standard 480x640.
    Provides context manager support for clean resource management.

    Attributes:
        device_id (int): Camera device ID (0 for first camera).
        cap (cv2.VideoCapture): OpenCV video capture object.
        target_height (int): Target frame height in pixels.
        target_width (int): Target frame width in pixels.

    Example:
        >>> with CameraCapture(device_id=0) as cam:
        ...     frame = cam.read()
        ...     print(frame.shape)  # (480, 640, 3)
    """

    def __init__(self, device_id: int = 0, height: int = 480, width: int = 640):
        """Initialize camera capture.

        Args:
            device_id: Camera device ID (0 is default/first camera).
            height: Target frame height (default 480).
            width: Target frame width (default 640).

        Raises:
            RuntimeError: If camera device cannot be opened.
        """
        self.device_id = device_id
        self.target_height = height
        self.target_width = width

        # Open camera
        self.cap = cv2.VideoCapture(device_id)

        # Verify camera opened successfully
        if not self.cap.isOpened():
            raise RuntimeError(
                f"Cannot open camera at device {device_id}. "
                "Ensure camera is connected and not in use."
            )

    def read(self) -> np.ndarray:
        """Read and return a frame from camera.

        Captures frame from camera and resizes to target dimensions.

        Returns:
            Frame as numpy array with shape (height, width, 3) in BGR format.

        Raises:
            RuntimeError: If frame capture fails.

        Example:
            >>> cam = CameraCapture()
            >>> frame = cam.read()
            >>> frame.shape
            (480, 640, 3)
        """
        ret, frame = self.cap.read()

        if not ret:
            raise RuntimeError(
                "Failed to read frame from camera. "
                "Camera may have been disconnected."
            )

        # Resize to target dimensions
        resized_frame = cv2.resize(frame, (self.target_width, self.target_height))

        return resized_frame

    def release(self) -> None:
        """Release camera resource.

        Must be called when done with camera to free resources.
        Automatically called when using context manager.
        """
        if self.cap is not None:
            self.cap.release()

    def __enter__(self) -> "CameraCapture":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - release camera."""
        self.release()

    def __del__(self):
        """Destructor - ensure camera is released."""
        self.release()


def get_camera(device_id: int = 0) -> CameraCapture:
    """Factory function to create camera capture instance.

    Args:
        device_id: Camera device ID.

    Returns:
        CameraCapture instance.

    Raises:
        RuntimeError: If camera cannot be opened.
    """
    return CameraCapture(device_id=device_id)
