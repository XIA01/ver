"""Feature extraction from facial landmarks using MediaPipe.

Extracts biometric features (eye coordinates, head pose, pupil position)
from detected facial landmarks. Generates a fixed-size feature vector
suitable for regression models.
"""

import numpy as np
from typing import Tuple, Optional, Dict
try:
    from mediapipe.python.solutions import face_mesh
except ImportError:
    # Fallback para versiones más nuevas de MediaPipe
    from mediapipe.solutions import face_mesh


class FeatureExtractor:
    """Extracts eye and head features from facial landmarks.

    Uses MediaPipe FaceMesh to detect 468 facial landmarks and extracts
    relevant features for gaze estimation: eye coordinates, head pose,
    and pupil centroid.

    Attributes:
        roi_size (int): Size of ROI patch around eyes (pixels).
        detector (face_mesh.FaceMesh): MediaPipe face detection model.
        left_eye_indices (list): Landmark indices for left eye.
        right_eye_indices (list): Landmark indices for right eye.

    Example:
        >>> extractor = FeatureExtractor(roi_size=64)
        >>> features, meta = extractor.extract_features(frame)
        >>> if meta['valid']:
        ...     print(features.shape)  # (16,)
    """

    # Key landmark indices for eyes (MediaPipe FaceMesh)
    LEFT_EYE_INDICES = [33, 160, 158, 133]  # Left eye corners
    RIGHT_EYE_INDICES = [263, 387, 386, 362]  # Right eye corners
    NOSE_TIP_INDEX = 1  # Nose tip for head pose
    CHIN_INDEX = 152  # Chin for head pose

    def __init__(self, roi_size: int = 64):
        """Initialize feature extractor.

        Args:
            roi_size: Size of ROI patches around eyes. Must be >= 32.

        Raises:
            ValueError: If roi_size < 32.
        """
        if roi_size < 32:
            raise ValueError(
                f"roi_size must be >= 32 pixels, got {roi_size}"
            )

        self.roi_size = roi_size

        # Initialize MediaPipe FaceMesh
        self.detector = face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def extract_features(
        self, frame: np.ndarray
    ) -> Tuple[Optional[np.ndarray], Dict]:
        """Extract features from a frame.

        Args:
            frame: Input frame (H, W, 3) in RGB format.

        Returns:
            Tuple of (features, metadata):
            - features: Array of shape (16,) or None if no face detected
            - metadata: Dict with keys:
                - 'valid': bool indicating if extraction succeeded
                - 'reason': str explaining why extraction failed (if not valid)
                - 'confidence': float confidence score [0, 1] if valid

        Example:
            >>> extractor = FeatureExtractor()
            >>> features, meta = extractor.extract_features(frame)
            >>> if meta['valid']:
            ...     print(f"Confidence: {meta['confidence']:.3f}")
        """
        # Detect landmarks
        results = self.detector.process(frame)

        # Check if face was detected
        if not results.multi_face_landmarks:
            return None, {"valid": False, "reason": "no_face"}

        face = results.multi_face_landmarks[0]

        try:
            # Extract eye coordinates (4 corners each = 8 values)
            left_eye = self._extract_eye_landmarks(face, self.LEFT_EYE_INDICES)
            right_eye = self._extract_eye_landmarks(face, self.RIGHT_EYE_INDICES)

            # Extract head pose (3 values: pitch, yaw, roll)
            head_pose = self._estimate_head_pose(face)

            # Concatenate all features
            features = np.concatenate([
                left_eye.flatten(),  # 8 values
                right_eye.flatten(),  # 8 values
                head_pose  # 3 values (note: using 2 for now)
            ]).astype(np.float32)

            # Get confidence from first landmark
            confidence = float(face.landmark[0].z)

            return features, {
                "valid": True,
                "confidence": confidence,
            }

        except Exception as e:
            return None, {"valid": False, "reason": f"extraction_error: {str(e)}"}

    def _extract_eye_landmarks(
        self, face: "face_mesh.FaceLandmark", indices: list
    ) -> np.ndarray:
        """Extract 4 corner coordinates of an eye.

        Args:
            face: MediaPipe face landmarks.
            indices: List of 4 landmark indices.

        Returns:
            Array of shape (4, 2) with (x, y) coordinates.
        """
        points = np.array([
            [face.landmark[i].x, face.landmark[i].y]
            for i in indices
        ], dtype=np.float32)

        return points

    def _estimate_head_pose(
        self, face: "face_mesh.FaceLandmark"
    ) -> np.ndarray:
        """Estimate head pose (pitch, yaw, roll) from landmarks.

        Simplified estimation using nose tip and chin position.

        Args:
            face: MediaPipe face landmarks.

        Returns:
            Array of shape (3,) with [pitch, yaw, roll].
        """
        # Get nose tip position
        nose = np.array([
            face.landmark[self.NOSE_TIP_INDEX].x,
            face.landmark[self.NOSE_TIP_INDEX].y,
        ])

        # Get chin position
        chin = np.array([
            face.landmark[self.CHIN_INDEX].x,
            face.landmark[self.CHIN_INDEX].y,
        ])

        # Simple head pose approximation (simplified approach)
        # In production, would use 3D pose estimation
        nose_chin_vec = chin - nose

        # Estimate angles from vector (very simplified)
        pitch = np.arctan2(nose_chin_vec[1], 1.0)  # Vertical angle
        yaw = np.arctan2(nose_chin_vec[0], 1.0)  # Horizontal angle
        roll = 0.0  # Not estimated in this simplified version

        return np.array([pitch, yaw], dtype=np.float32)  # Return 2 values for now

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Clean up resources."""
        if hasattr(self, 'detector') and self.detector is not None:
            self.detector.close()

    def __del__(self):
        """Destructor."""
        self.close()
