"""PyQt6 overlay application for gaze tracking visualization.

Renders transparent overlay with tracking squares on top of desktop.
"""

import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import pyqtSignal
import threading
from typing import Optional, Tuple


class GazeOverlay(QWidget):
    """Transparent overlay widget for gaze tracking visualization.

    Displays:
    - Red target square (calibration)
    - Green prediction square (where model thinks you're looking)
    - Confidence indicator (size/opacity)
    """

    # Signals for thread-safe updates
    update_position = pyqtSignal(int, int)
    update_target = pyqtSignal(int, int)

    def __init__(self):
        """Initialize overlay window."""
        super().__init__()

        # Window properties
        self.setWindowTitle("GAZE-INFERENCE Overlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Get screen geometry
        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.geometry()
        self.setGeometry(self.screen_geometry)

        # Tracking state
        self.green_pos = QPoint(self.screen_geometry.width() // 2,
                               self.screen_geometry.height() // 2)
        self.target_pos = None
        self.square_size = 50
        self.confidence = 0.5

        # Colors
        self.color_green = QColor(0, 255, 0)
        self.color_red = QColor(255, 0, 0)
        self.color_text = QColor(255, 255, 255)

        # Connect signals
        self.update_position.connect(self._on_update_position)
        self.update_target.connect(self._on_update_target)

        # Setup timer for smoothing (20ms = 50fps)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20)

    def _on_update_position(self, x: int, y: int):
        """Update green square position."""
        self.green_pos = QPoint(x, y)
        self.update()

    def _on_update_target(self, x: int, y: int):
        """Update target (red) square position."""
        self.target_pos = QPoint(x, y)
        self.update()

    def set_prediction(self, x: float, y: float, confidence: float = 0.5):
        """Set green square position (normalized 0-1).

        Args:
            x: Normalized x position (0-1)
            y: Normalized y position (0-1)
            confidence: Confidence score (0-1)
        """
        screen_x = int(x * self.screen_geometry.width())
        screen_y = int(y * self.screen_geometry.height())
        self.confidence = confidence
        self.update_position.emit(screen_x, screen_y)

    def set_target(self, x: float, y: float):
        """Set target square position (normalized 0-1).

        Args:
            x: Normalized x position (0-1)
            y: Normalized y position (0-1)
        """
        screen_x = int(x * self.screen_geometry.width())
        screen_y = int(y * self.screen_geometry.height())
        self.update_target.emit(screen_x, screen_y)

    def paintEvent(self, event):
        """Paint the overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw target square (red) if set
        if self.target_pos is not None:
            self._draw_square(painter, self.target_pos, 60, self.color_red)

        # Draw prediction square (green)
        size = int(self.square_size * (1.0 + self.confidence))
        self._draw_square(painter, self.green_pos, size, self.color_green)

        # Draw confidence text
        font = QFont("Monospace", 10)
        painter.setFont(font)
        painter.setPen(self.color_text)
        text = f"Conf: {self.confidence:.2f}"
        painter.drawText(10, 30, 200, 30, Qt.AlignmentFlag.AlignLeft, text)

    def _draw_square(self, painter: QPainter, center: QPoint,
                    size: int, color: QColor):
        """Draw a square at given center position.

        Args:
            painter: QPainter instance
            center: Center position of square
            size: Side length of square
            color: Color to draw
        """
        half_size = size // 2
        rect = QRect(center.x() - half_size, center.y() - half_size, size, size)

        # Draw filled rectangle
        painter.fillRect(rect, color)

        # Draw border
        pen = QPen(color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(rect)

    def closeEvent(self, event):
        """Handle window close."""
        self.timer.stop()
        event.accept()


class OverlayManager:
    """Manages overlay window lifecycle."""

    def __init__(self):
        """Initialize overlay manager."""
        self.app = None
        self.overlay = None
        self.thread = None

    def start(self):
        """Start overlay in separate thread."""
        self.thread = threading.Thread(target=self._run_qt, daemon=True)
        self.thread.start()

        # Wait for overlay to be ready
        import time
        for _ in range(100):
            if self.overlay is not None:
                time.sleep(0.1)
                return True
            time.sleep(0.01)

        return False

    def _run_qt(self):
        """Run Qt event loop in thread."""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)

        self.overlay = GazeOverlay()
        self.overlay.show()

        # Run event loop
        self.app.exec()

    def update_prediction(self, x: float, y: float, confidence: float = 0.5):
        """Update prediction position.

        Args:
            x: Normalized x (0-1)
            y: Normalized y (0-1)
            confidence: Confidence (0-1)
        """
        if self.overlay:
            self.overlay.set_prediction(x, y, confidence)

    def set_target(self, x: float, y: float):
        """Set target position.

        Args:
            x: Normalized x (0-1)
            y: Normalized y (0-1)
        """
        if self.overlay:
            self.overlay.set_target(x, y)

    def stop(self):
        """Stop overlay."""
        if self.app:
            self.app.quit()
        if self.thread:
            self.thread.join(timeout=2)
