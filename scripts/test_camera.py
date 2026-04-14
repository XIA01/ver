#!/usr/bin/env python3
"""Quick camera diagnostic."""

import sys
import cv2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.sensorium.camera import CameraCapture

print("📸 Camera Diagnostic Test")
print("=" * 50)

# Test camera
try:
    cam = CameraCapture()
    print("✅ Camera initialized")

    # Capture 5 frames
    for i in range(5):
        frame = cam.read()
        print(f"   Frame {i+1}: shape={frame.shape}, dtype={frame.dtype}, min={frame.min()}, max={frame.max()}")

    # Save one frame
    frame = cam.read()
    output_path = "test_frame.jpg"
    cv2.imwrite(output_path, frame)
    print(f"✅ Frame saved to {output_path}")

    cam.release()
    print("✅ Camera released")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
