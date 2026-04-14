#!/usr/bin/env python3
"""🎯 GAZE-INFERENCE Phase 0 - Web Real-time Viewer

Abre en navegador: http://localhost:5000
Verás tu cara en TIEMPO REAL con detección de nariz
"""

import sys
import cv2
import threading
import time
from pathlib import Path
from flask import Flask, render_template_string, Response

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.sensorium.camera import CameraCapture

app = Flask(__name__)

# Global state
camera = None
face_cascade = None
frame_lock = threading.Lock()
current_frame = None
stats = {
    'fps': 0,
    'latency': 0,
    'detected': False,
    'frame_count': 0,
    'detection_rate': 0
}


def init_detectors():
    """Initialize camera and face detector."""
    global camera, face_cascade

    camera = CameraCapture()
    cascade_path = cv2.data.haarcascades
    face_cascade = cv2.CascadeClassifier(
        cascade_path + 'haarcascade_frontalface_default.xml'
    )


def detect_nose(frame):
    """Detect face and nose position."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))

    if len(faces) == 0:
        return None, None

    fx, fy, fw, fh = faces[0]
    nose_x = (fx + fw/2) / frame.shape[1]
    # Punta de nariz está ~50-55% hacia abajo de la cara (no 40%)
    nose_y = (fy + fh * 0.52) / frame.shape[0]

    return nose_x, nose_y, (fx, fy, fw, fh)


def capture_frames():
    """Capture frames from camera continuously."""
    global current_frame, stats

    previous_pos = None
    frame_count = 0
    fps_time = time.time()
    fps = 0
    detected_count = 0

    try:
        while True:
            frame = camera.read()
            frame_count += 1
            start_time = time.perf_counter()

            # Detect
            result = detect_nose(frame)
            if result and len(result) == 3:
                nose_x, nose_y, (fx, fy, fw, fh) = result
            else:
                nose_x, nose_y = None, None

            detected = nose_x is not None
            if detected:
                detected_count += 1

            # Draw
            display_frame = frame.copy()

            if nose_x is not None:
                # Draw face rect
                cv2.rectangle(display_frame, (fx, fy), (fx+fw, fy+fh), (100, 200, 255), 2)

                # Draw nose
                x = int(nose_x * frame.shape[1])
                y = int(nose_y * frame.shape[0])
                cv2.circle(display_frame, (x, y), 10, (0, 255, 0), -1)
                cv2.circle(display_frame, (x, y), 15, (0, 255, 0), 2)

            # FPS calc
            if frame_count % 15 == 0:
                now = time.time()
                fps = 15 / (now - fps_time)
                fps_time = now

            latency = (time.perf_counter() - start_time) * 1000

            # Draw info
            cv2.putText(display_frame, f"FPS: {fps:.1f}", (15, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Latency: {latency:.2f}ms", (15, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            status = "✅ DETECTED" if nose_x else "❌ NO FACE"
            color = (0, 255, 0) if nose_x else (0, 0, 255)
            cv2.putText(display_frame, status, (15, 105),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if frame_count > 0:
                detection_rate = (detected_count / frame_count * 100)
                cv2.putText(display_frame, f"Detection: {detection_rate:.0f}%", (15, 140),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Update global frame
            with frame_lock:
                current_frame = display_frame
                stats['fps'] = fps
                stats['latency'] = latency
                stats['detected'] = detected
                stats['frame_count'] = frame_count
                stats['detection_rate'] = detection_rate if frame_count > 0 else 0

    except Exception as e:
        print(f"Error in capture thread: {e}")


def generate_frames():
    """Generator for video stream."""
    while True:
        with frame_lock:
            if current_frame is None:
                continue

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', current_frame)
            frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n' +
               frame_bytes + b'\r\n')


@app.route('/')
def index():
    """Main page."""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>👁️ GAZE-INFERENCE Phase 0 - Real-time Tracker</title>
        <style>
            body {
                font-family: 'Courier New', monospace;
                background: #0a0a0a;
                color: #00ff00;
                padding: 20px;
                margin: 0;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
            }
            h1 {
                text-align: center;
                color: #00ff00;
                font-size: 2em;
                margin: 0 0 20px 0;
            }
            .video-container {
                background: #1a1a1a;
                border: 2px solid #00ff00;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 20px;
                text-align: center;
            }
            img {
                max-width: 100%;
                height: auto;
                border-radius: 3px;
            }
            .stats {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-top: 20px;
            }
            .stat-box {
                background: #1a1a1a;
                border: 1px solid #00ff00;
                border-radius: 3px;
                padding: 15px;
                text-align: center;
            }
            .stat-label {
                font-size: 0.9em;
                color: #888;
                margin-bottom: 5px;
            }
            .stat-value {
                font-size: 1.5em;
                color: #00ff00;
                font-weight: bold;
            }
            .info {
                background: #1a1a1a;
                border-left: 3px solid #00ff00;
                padding: 15px;
                margin-top: 20px;
                line-height: 1.6;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👁️ GAZE-INFERENCE Phase 0</h1>
            <h2 style="text-align: center; margin-top: 0;">Real-time Face & Nose Detection</h2>

            <div class="video-container">
                <img src="/video_feed" alt="Video Stream">
            </div>

            <div class="stats">
                <div class="stat-box">
                    <div class="stat-label">FPS</div>
                    <div class="stat-value" id="fps">--</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Latency (ms)</div>
                    <div class="stat-value" id="latency">--</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Status</div>
                    <div class="stat-value" id="status">--</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Detection Rate</div>
                    <div class="stat-value" id="detection">--</div>
                </div>
            </div>

            <div class="info">
                <strong>📊 Información:</strong><br>
                ✅ Cámara detectando en tiempo real<br>
                ✅ Círculo VERDE = Posición de nariz detectada<br>
                ✅ Rectángulo naranja = Bounding box de cara<br>
                ✅ Latencia &lt; 10ms (excelente)<br>
                <br>
                <strong>🎯 Siguiente: Phase 1</strong><br>
                Mostrar target rojo y calibrar modelo
            </div>
        </div>

        <script>
            // Update stats every 500ms
            setInterval(() => {
                fetch('/api/stats')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('fps').textContent = data.fps.toFixed(1);
                        document.getElementById('latency').textContent = data.latency.toFixed(2);
                        document.getElementById('status').textContent = data.detected ? '✅ DETECTED' : '❌ NO FACE';
                        document.getElementById('detection').textContent = data.detection_rate.toFixed(0) + '%';
                    });
            }, 500);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)


@app.route('/video_feed')
def video_feed():
    """Video stream route."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/api/stats')
def api_stats():
    """API endpoint for stats."""
    return stats


def main():
    """Main function."""
    print("=" * 70)
    print("🎯 GAZE-INFERENCE Phase 0 - Web Real-time")
    print("=" * 70)

    print("[1/2] Initializing camera and detectors...")
    init_detectors()
    print("     ✅ Camera ready")
    print("     ✅ Face detector loaded")

    print("[2/2] Starting capture thread...")
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()
    print("     ✅ Capture thread running")

    print("-" * 70)
    print("🌐 Starting web server...")
    print("   📱 Open your browser: http://localhost:8080")
    print("   ⏹️  Press Ctrl+C to stop")
    print("-" * 70)

    try:
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down...")
    finally:
        camera.release()
        print("✅ Resources released")


if __name__ == '__main__':
    main()
