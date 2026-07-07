"""
Mobile Communication System Simulator
Entry point with splash screen.
"""
import sys
import math
from PySide6.QtWidgets import QApplication, QSplashScreen, QWidget
from PySide6.QtCore import Qt, QTimer, QElapsedTimer
from PySide6.QtGui import (QPixmap, QPainter, QColor, QLinearGradient,
                             QBrush, QPen, QFont, QPainterPath)


class SplashScreen(QSplashScreen):
    """Professional animated splash screen."""

    def __init__(self):
        # Create pixmap
        pm = QPixmap(700, 400)
        pm.fill(QColor("#050810"))
        super().__init__(pm, Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self._progress = 0
        self._phase = 0
        self._message = "Initializing..."

        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start(30)

    def _animate(self):
        self._phase += 3
        self.repaint()

    def set_progress(self, value: int, message: str = ""):
        self._progress = value
        if message:
            self._message = message
        self.repaint()

    def drawContents(self, painter: QPainter):
        w, h = self.width(), self.height()

        # Background gradient
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor("#040608"))
        grad.setColorAt(0.5, QColor("#0A0E1A"))
        grad.setColorAt(1.0, QColor("#050810"))
        painter.fillRect(0, 0, w, h, QBrush(grad))

        # Animated concentric rings
        for i in range(4):
            r = 80 + i * 40
            alpha = int(20 + 15 * math.sin(math.radians(self._phase + i * 60)))
            c = QColor("#00D4FF")
            c.setAlpha(alpha)
            painter.setPen(QPen(c, 1.2))
            painter.drawEllipse(w//2 - r, h//2 - r - 30, 2*r, 2*r)

        # Animated wave lines at bottom
        for j in range(3):
            path = QPainterPath()
            amp = 12 + j * 5
            y_base = h - 60 - j * 18
            path.moveTo(0, y_base)
            for x in range(0, w + 10, 4):
                y = y_base + amp * math.sin(x * 0.015 + math.radians(self._phase + j * 40))
                path.lineTo(x, y)
            c = QColor(["#00D4FF", "#7B2FFF", "#00FF88"][j])
            c.setAlpha(40 - j * 10)
            painter.setPen(QPen(c, 1.0))
            painter.drawPath(path)

        # Center icon / logo mark
        cx, cy = w // 2, h // 2 - 30
        pulse = int(200 + 55 * math.sin(math.radians(self._phase * 2)))
        c_center = QColor("#00D4FF")
        c_center.setAlpha(pulse)
        painter.setBrush(QBrush(c_center))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 24, cy - 24, 48, 48)

        # Inner white dot
        painter.setBrush(QBrush(QColor("#E8F0FF")))
        painter.drawEllipse(cx - 6, cy - 6, 12, 12)

        # Title
        painter.setPen(QPen(QColor("#E8F0FF")))
        font = QFont("Segoe UI", 24, QFont.Bold)
        painter.setFont(font)
        title_rect = painter.fontMetrics().boundingRect("Mobile Communication")
        painter.drawText((w - title_rect.width()) // 2, cy + 60, "Mobile Communication")

        painter.setPen(QPen(QColor("#00D4FF")))
        font2 = QFont("Segoe UI", 24, QFont.Bold)
        painter.setFont(font2)
        sub_rect = painter.fontMetrics().boundingRect("System Simulator")
        painter.drawText((w - sub_rect.width()) // 2, cy + 92, "System Simulator")

        # Tagline
        painter.setPen(QPen(QColor("#4A5680")))
        font3 = QFont("Segoe UI", 9)
        font3.setLetterSpacing(QFont.AbsoluteSpacing, 3.0)
        painter.setFont(font3)
        tag = "GRADUATION PROJECT  ·  LTE / 5G NR SIMULATION PLATFORM"
        tag_rect = painter.fontMetrics().boundingRect(tag)
        painter.drawText((w - tag_rect.width()) // 2, cy + 118, tag)

        # Progress bar background
        bar_x, bar_y = 80, h - 50
        bar_w, bar_h = w - 160, 6
        painter.setBrush(QBrush(QColor("#1A2A4A")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)

        # Progress fill
        fill_w = int(bar_w * self._progress / 100)
        if fill_w > 0:
            grad2 = QLinearGradient(bar_x, 0, bar_x + bar_w, 0)
            grad2.setColorAt(0, QColor("#0060AA"))
            grad2.setColorAt(1, QColor("#00D4FF"))
            painter.setBrush(QBrush(grad2))
            painter.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 3, 3)

        # Progress % text
        painter.setPen(QPen(QColor("#00D4FF")))
        font4 = QFont("Segoe UI", 8, QFont.Bold)
        painter.setFont(font4)
        pct_text = f"{self._progress}%"
        pct_rect = painter.fontMetrics().boundingRect(pct_text)
        painter.drawText(bar_x + fill_w - pct_rect.width() // 2,
                          bar_y - 4, pct_text)

        # Message
        painter.setPen(QPen(QColor("#4A5680")))
        font5 = QFont("Segoe UI", 9)
        painter.setFont(font5)
        msg_rect = painter.fontMetrics().boundingRect(self._message)
        painter.drawText((w - msg_rect.width()) // 2, h - 20, self._message)


def run_loading_sequence(splash: SplashScreen, app: QApplication):
    """Simulate loading sequence."""
    steps = [
        (5,  "Initializing core modules..."),
        (15, "Loading channel models..."),
        (25, "Configuring modulation codecs..."),
        (35, "Setting up network topology engine..."),
        (50, "Initializing mobility model..."),
        (60, "Loading AI handover predictor..."),
        (70, "Building GUI components..."),
        (80, "Configuring scheduler..."),
        (90, "Preparing plots engine..."),
        (100, "Ready!"),
    ]
    for progress, message in steps:
        splash.set_progress(progress, message)
        app.processEvents()
        # Small delay
        timer = QElapsedTimer()
        timer.start()
        while timer.elapsed() < 120:
            app.processEvents()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mobile Communication System Simulator")
    app.setOrganizationName("CommSim")
    app.setApplicationVersion("2.0")

    # High DPI support
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Show splash
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    # Loading sequence
    run_loading_sequence(splash, app)

    # Import and create main window
    from gui.main_window import MainWindow
    window = MainWindow()

    # Close splash and show main window
    splash._anim_timer.stop()
    splash.finish(window)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
