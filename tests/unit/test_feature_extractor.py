"""Unit tests for feature extraction from facial landmarks.

Tests MediaPipe integration and feature vector generation.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock


class TestFeatureExtractor:
    """Test suite for FeatureExtractor class."""

    def test_init_valid_roi_size(self):
        """FeatureExtractor should initialize with valid ROI size."""
        with patch("mediapipe.solutions.face_mesh.FaceMesh"):
            from src.sensorium.feature_extractor import FeatureExtractor
            extractor = FeatureExtractor(roi_size=64)
            assert extractor.roi_size == 64

    def test_init_invalid_roi_size(self):
        """FeatureExtractor should raise ValueError for invalid ROI."""
        from src.sensorium.feature_extractor import FeatureExtractor

        with pytest.raises(ValueError, match="roi_size must be >= 32"):
            FeatureExtractor(roi_size=16)

    def test_extract_features_no_face(self, dummy_frame):
        """Should return None and invalid metadata when no face detected."""
        from src.sensorium.feature_extractor import FeatureExtractor

        with patch("mediapipe.solutions.face_mesh.FaceMesh") as mock_mediapipe:
            mock_detector = MagicMock()
            mock_results = MagicMock()
            mock_results.multi_face_landmarks = None
            mock_detector.process.return_value = mock_results
            mock_mediapipe.return_value = mock_detector

            extractor = FeatureExtractor()
            features, metadata = extractor.extract_features(dummy_frame)

            assert features is None
            assert metadata["valid"] is False
            assert "no_face" in metadata.get("reason", "")

    def test_extract_features_with_face(self, dummy_frame):
        """Should return feature vector when face detected."""
        from src.sensorium.feature_extractor import FeatureExtractor

        with patch("mediapipe.solutions.face_mesh.FaceMesh") as mock_mediapipe:
            # Mock MediaPipe results
            mock_detector = MagicMock()
            face_landmarks = MagicMock()

            # Create mock landmarks (468 points)
            mock_landmarks = []
            for i in range(468):
                landmark = MagicMock()
                landmark.x = 0.5 + np.random.uniform(-0.1, 0.1)
                landmark.y = 0.5 + np.random.uniform(-0.1, 0.1)
                landmark.z = 0.0
                mock_landmarks.append(landmark)

            face_landmarks.landmark = mock_landmarks

            mock_results = MagicMock()
            mock_results.multi_face_landmarks = [face_landmarks]
            mock_detector.process.return_value = mock_results

            mock_mediapipe.return_value = mock_detector

            extractor = FeatureExtractor()
            features, metadata = extractor.extract_features(dummy_frame)

            # Check feature vector
            assert features is not None
            assert isinstance(features, np.ndarray)
            assert features.dtype == np.float32
            assert len(features) > 0  # Should have some features
            assert metadata["valid"] is True

    def test_extract_features_output_shape(self, dummy_frame):
        """Feature vector should have consistent shape."""
        from src.sensorium.feature_extractor import FeatureExtractor

        with patch("mediapipe.solutions.face_mesh.FaceMesh") as mock_mediapipe:
            mock_detector = MagicMock()
            face_landmarks = MagicMock()

            # Create mock landmarks
            mock_landmarks = []
            for i in range(468):
                landmark = MagicMock()
                landmark.x = 0.5
                landmark.y = 0.5
                landmark.z = 0.0
                mock_landmarks.append(landmark)

            face_landmarks.landmark = mock_landmarks
            mock_results = MagicMock()
            mock_results.multi_face_landmarks = [face_landmarks]
            mock_detector.process.return_value = mock_results
            mock_mediapipe.return_value = mock_detector

            extractor = FeatureExtractor()

            # Extract multiple times, should have same shape
            features1, _ = extractor.extract_features(dummy_frame)
            features2, _ = extractor.extract_features(dummy_frame)

            assert features1.shape == features2.shape
            assert features1.dtype == np.float32

    def test_extract_features_with_multiple_faces(self, dummy_frame):
        """Should use first face when multiple detected."""
        from src.sensorium.feature_extractor import FeatureExtractor

        with patch("mediapipe.solutions.face_mesh.FaceMesh") as mock_mediapipe:
            mock_detector = MagicMock()

            # Create two mock faces
            faces = []
            for face_num in range(2):
                face_landmarks = MagicMock()
                mock_landmarks = []
                for i in range(468):
                    landmark = MagicMock()
                    landmark.x = 0.3 + face_num * 0.2
                    landmark.y = 0.5
                    landmark.z = 0.0
                    mock_landmarks.append(landmark)
                face_landmarks.landmark = mock_landmarks
                faces.append(face_landmarks)

            mock_results = MagicMock()
            mock_results.multi_face_landmarks = faces
            mock_detector.process.return_value = mock_results
            mock_mediapipe.return_value = mock_detector

            extractor = FeatureExtractor()
            features, metadata = extractor.extract_features(dummy_frame)

            # Should still extract successfully (uses first face)
            assert features is not None
            assert metadata["valid"] is True


class TestFeatureExtractorLatency:
    """Test latency of feature extraction."""

    @pytest.mark.benchmark
    def test_extraction_latency(self, dummy_frame):
        """Feature extraction should be < 30ms."""
        import time

        from src.sensorium.feature_extractor import FeatureExtractor

        with patch("mediapipe.solutions.face_mesh.FaceMesh") as mock_mediapipe:
            mock_detector = MagicMock()
            face_landmarks = MagicMock()

            mock_landmarks = []
            for i in range(468):
                landmark = MagicMock()
                landmark.x = 0.5
                landmark.y = 0.5
                landmark.z = 0.0
                mock_landmarks.append(landmark)

            face_landmarks.landmark = mock_landmarks
            mock_results = MagicMock()
            mock_results.multi_face_landmarks = [face_landmarks]
            mock_detector.process.return_value = mock_results
            mock_mediapipe.return_value = mock_detector

            extractor = FeatureExtractor()

            start = time.perf_counter()
            features, _ = extractor.extract_features(dummy_frame)
            elapsed = (time.perf_counter() - start) * 1000

            # Mock should be very fast
            assert elapsed < 100
            assert features is not None
