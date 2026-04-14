"""Unit tests for camera capture module (sensorium.camera).

Tests camera initialization, frame reading, and error handling.
No real hardware required (uses mocks).
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys


class TestCameraCapture:
    """Test suite for CameraCapture class."""

    def test_camera_init_success(self):
        """Camera should initialize without errors with valid device."""
        with patch('cv2.VideoCapture') as mock_cv2:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_cv2.return_value = mock_cap

            from src.sensorium.camera import CameraCapture
            cam = CameraCapture(device_id=0)

            assert cam is not None
            mock_cv2.assert_called_once_with(0)

    def test_camera_init_device_not_opened(self):
        """Camera init should raise RuntimeError if device not opened."""
        with patch('cv2.VideoCapture') as mock_cv2:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = False
            mock_cv2.return_value = mock_cap

            from src.sensorium.camera import CameraCapture

            with pytest.raises(RuntimeError, match="Cannot open camera"):
                CameraCapture(device_id=0)

    def test_read_frame_valid(self):
        """Read should return frame with shape (480, 640, 3)."""
        with patch('cv2.VideoCapture') as mock_cv2:
            with patch('cv2.resize') as mock_resize:
                mock_cap = MagicMock()
                mock_cap.isOpened.return_value = True
                mock_cap.read.return_value = (True, np.zeros((720, 1280, 3), dtype=np.uint8))
                mock_cv2.return_value = mock_cap

                mock_resize.return_value = np.zeros((480, 640, 3), dtype=np.uint8)

                from src.sensorium.camera import CameraCapture
                cam = CameraCapture(device_id=0)
                frame = cam.read()

                assert frame.shape == (480, 640, 3)
                assert frame.dtype == np.uint8

    def test_read_frame_failure(self):
        """Read should raise RuntimeError if frame read fails."""
        with patch('cv2.VideoCapture') as mock_cv2:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_cap.read.return_value = (False, None)
            mock_cv2.return_value = mock_cap

            from src.sensorium.camera import CameraCapture
            cam = CameraCapture(device_id=0)

            with pytest.raises(RuntimeError, match="Failed to read frame"):
                cam.read()

    def test_release_camera(self):
        """Release should call cv2.VideoCapture.release()."""
        with patch('cv2.VideoCapture') as mock_cv2:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_cv2.return_value = mock_cap

            from src.sensorium.camera import CameraCapture
            cam = CameraCapture(device_id=0)
            cam.release()

            mock_cap.release.assert_called_once()

    def test_context_manager(self):
        """Camera should work as context manager."""
        with patch('cv2.VideoCapture') as mock_cv2:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_cap.read.return_value = (True, np.zeros((720, 1280, 3), dtype=np.uint8))
            mock_cv2.return_value = mock_cap

            with patch('cv2.resize') as mock_resize:
                mock_resize.return_value = np.zeros((480, 640, 3), dtype=np.uint8)

                from src.sensorium.camera import CameraCapture

                with CameraCapture(device_id=0) as cam:
                    frame = cam.read()
                    assert frame.shape == (480, 640, 3)

                # Should call release after context exit
                mock_cap.release.assert_called()


class TestCameraLatency:
    """Test latency of camera operations."""

    @pytest.mark.benchmark
    def test_read_latency(self):
        """Camera read should complete in < 50ms (mock latency test)."""
        import time

        with patch('cv2.VideoCapture') as mock_cv2:
            with patch('cv2.resize') as mock_resize:
                mock_cap = MagicMock()
                mock_cap.isOpened.return_value = True
                mock_cap.read.return_value = (True, np.zeros((720, 1280, 3), dtype=np.uint8))
                mock_cv2.return_value = mock_cap
                mock_resize.return_value = np.zeros((480, 640, 3), dtype=np.uint8)

                from src.sensorium.camera import CameraCapture
                cam = CameraCapture(device_id=0)

                start = time.perf_counter()
                frame = cam.read()
                elapsed = (time.perf_counter() - start) * 1000

                # Mock is fast, but real camera should be < 50ms
                assert elapsed < 100  # Generous for mock
                assert frame.shape == (480, 640, 3)
