#!/usr/bin/env python3
"""Main application: Gaze tracking with live visualization.

Reads from camera, detects nose position, displays green square following it.
"""

import sys
import time
import numpy as np
import cv2
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sensorium.camera import CameraCapture
from src.overlay.qt_app import OverlayManager


def get_nose_position(frame: np.ndarray) -> tuple:
    """Extract nose position from frame using MediaPipe.

    Args:
        frame: Input frame (H, W, 3) BGR

    Returns:
        Tuple of (x_norm, y_norm) in [0, 1] range
    """
    import mediapipe as mp

    # Initialize MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        min_detection_confidence=0.5,
    )

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect landmarks
    results = face_mesh.process(rgb_frame)

    if not results.multi_face_landmarks:
        return None, None

    # Get nose tip (landmark index 1)
    nose = results.multi_face_landmarks[0].landmark[1]

    return nose.x, nose.y


def smooth_position(current: tuple, previous: tuple, alpha: float = 0.3) -> tuple:
    """Smooth position using exponential moving average.

    Args:
        current: Current position (x, y)
        previous: Previous position (x, y)
        alpha: Smoothing factor (0-1)

    Returns:
        Smoothed position (x, y)
    """
    if previous is None:
        return current

    x = alpha * current[0] + (1 - alpha) * previous[0]
    y = alpha * current[1] + (1 - alpha) * previous[1]

    return x, y


def main():
    """Main application loop."""
    print("🚀 GAZE-INFERENCE v0.0.1 - Phase 0: Latency Validation")
    print("=" * 60)

    # Initialize components
    print("[1/3] Initializing camera...")
    try:
        camera = CameraCapture(device_id=0)
        print("✅ Camera ready (480x640 @ 30fps)")
    except RuntimeError as e:
        print(f"❌ Camera error: {e}")
        return

    print("[2/3] Starting overlay...")
    overlay = OverlayManager()
    if not overlay.start():
        print("❌ Failed to start overlay")
        camera.release()
        return
    print("✅ Overlay ready (transparent, always-on-top)")

    print("[3/3] Starting tracking loop...")
    print("-" * 60)
    print("Press ESC to exit")
    print("-" * 60)

    # Tracking state
    previous_pos = None
    frame_count = 0
    fps_time = time.time()
    fps = 0

    try:
        while True:
            # Read frame
            try:
                frame = camera.read()
            except RuntimeError:
                print("❌ Camera disconnected")
                break

            frame_count += 1

            # Get nose position
            nose_x, nose_y = get_nose_position(frame)

            if nose_x is not None:
                # Smooth position
                pos = smooth_position((nose_x, nose_y), previous_pos, alpha=0.4)
                previous_pos = pos

                # Update overlay (green square follows nose)
                confidence = 0.7  # Dummy confidence
                overlay.update_prediction(pos[0], pos[1], confidence)

                # Calculate FPS
                if frame_count % 30 == 0:
                    now = time.time()
                    fps = 30 / (now - fps_time)
                    fps_time = now

            # Display frame with nose point (for debugging)
            display_frame = frame.copy()
            if nose_x is not None:
                # Draw nose position on frame
                x = int(nose_x * frame.shape[1])
                y = int(nose_y * frame.shape[0])
                cv2.circle(display_frame, (x, y), 5, (0, 255, 0), -1)
                cv2.circle(display_frame, (x, y), 10, (0, 255, 0), 2)

            # Add FPS
            cv2.putText(
                display_frame,
                f"FPS: {fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            # Add status
            status = "✅ Tracking" if nose_x is not None else "❌ No face"
            cv2.putText(
                display_frame,
                status,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0) if nose_x else (0, 0, 255),
                2,
            )

            # Show frame
            cv2.imshow("GAZE-INFERENCE Debug View", display_frame)

            # ESC to exit
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("\n⏹️  Exiting...")
                break

            # Print stats every 30 frames
            if frame_count % 30 == 0:
                print(f"[Frame {frame_count}] FPS: {fps:.1f} | "
                      f"Status: {'✅ Tracking' if nose_x else '❌ No face'}")

    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")

    finally:
        # Cleanup
        print("\n[Cleanup]")
        camera.release()
        overlay.stop()
        cv2.destroyAllWindows()
        print("✅ All resources released")
        print("=" * 60)


if __name__ == "__main__":
    main()
