#!/usr/bin/env python3
"""🎯 GAZE-INFERENCE Phase 0 - Save frames to disk

Como OpenCV display no funciona en este sistema, guardamos frames
con detección para que veas las imágenes después.
"""

import sys
import time
import cv2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.sensorium.camera import CameraCapture

def init_haar_cascades():
    cascade_path = cv2.data.haarcascades
    face_cascade = cv2.CascadeClassifier(
        cascade_path + 'haarcascade_frontalface_default.xml'
    )
    return face_cascade

def detect_nose_position(frame, face_cascade):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))

    if len(faces) == 0:
        return None, None

    fx, fy, fw, fh = faces[0]
    nose_x = (fx + fw/2) / frame.shape[1]
    # Punta de nariz está ~52% hacia abajo de la cara (no 40%)
    nose_y = (fy + fh * 0.52) / frame.shape[0]

    return nose_x, nose_y

def smooth_position(current, previous, alpha=0.3):
    if previous is None or current is None:
        return current
    x = alpha * current[0] + (1 - alpha) * previous[0]
    y = alpha * current[1] + (1 - alpha) * previous[1]
    return (x, y)

def main():
    print("=" * 70)
    print("🎯  GAZE-INFERENCE v0.0.1 - Phase 0 (SAVING FRAMES)")
    print("=" * 70)

    # Create output dir
    output_dir = Path("output_frames")
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Saving frames to: {output_dir}/")

    # Initialize
    print("[1/2] Initializing camera...")
    camera = CameraCapture()
    print("     ✅ Camera ready")

    print("[2/2] Loading face detector...")
    face_cascade = init_haar_cascades()
    print("     ✅ Face detector ready")

    print("-" * 70)
    print("👁️  CAPTURING 30 FRAMES WITH DETECTION")
    print("-" * 70)

    previous_pos = None
    frame_count = 0
    fps_time = time.time()
    fps = 0
    detected_count = 0
    max_frames = 30

    try:
        while frame_count < max_frames:
            frame = camera.read()
            frame_count += 1
            start_time = time.perf_counter()

            # Detect
            nose_x, nose_y = detect_nose_position(frame, face_cascade)

            if nose_x is not None:
                pos = smooth_position((nose_x, nose_y), previous_pos, alpha=0.5)
                previous_pos = pos
                detected_count += 1
            else:
                pos = None

            # Draw
            display_frame = frame.copy()

            if nose_x is not None:
                x = int(nose_x * frame.shape[1])
                y = int(nose_y * frame.shape[0])
                cv2.circle(display_frame, (x, y), 8, (0, 255, 0), -1)
                cv2.circle(display_frame, (x, y), 12, (0, 255, 0), 2)

                if pos:
                    sx = int(pos[0] * frame.shape[1])
                    sy = int(pos[1] * frame.shape[0])
                    cv2.circle(display_frame, (sx, sy), 10, (255, 128, 0), 2)

            if frame_count % 10 == 0:
                now = time.time()
                fps = 10 / (now - fps_time)
                fps_time = now

            latency = (time.perf_counter() - start_time) * 1000

            # Info
            status = "✅ DETECTED" if nose_x else "❌ NO FACE"
            color = (0, 255, 0) if nose_x else (0, 0, 255)

            cv2.putText(display_frame, f"Frame: {frame_count}/{max_frames}", (15, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display_frame, f"FPS: {fps:.1f}", (15, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Latency: {latency:.2f}ms", (15, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, status, (15, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Save
            frame_path = output_dir / f"frame_{frame_count:03d}.jpg"
            cv2.imwrite(str(frame_path), display_frame)

            print(f"Frame {frame_count:2d}/{max_frames} | {status} | FPS: {fps:5.1f} | Latency: {latency:6.2f}ms | Saved: {frame_path.name}")

    except KeyboardInterrupt:
        print("\n⏹️  Interrupted")

    finally:
        camera.release()

        print("\n" + "=" * 70)
        print(f"📊 SUMMARY:")
        print(f"   Frames captured: {frame_count}")
        print(f"   Frames with detection: {detected_count}")
        print(f"   Detection rate: {(detected_count/frame_count*100):.1f}%")
        print(f"   Average FPS: {fps:.1f}")
        print(f"   Saved to: {output_dir}/")
        print(f"   View frames with: ls -lh output_frames/")
        print("=" * 70)
        print("✨ Done! Check output_frames/ for images with detected faces")

if __name__ == "__main__":
    main()
