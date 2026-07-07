"""
Reusable custom widgets for the application.
"""
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                                  QFrame, QSizePolicy, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import (QColor, QPainter, QLinearGradient, QPen, QFont,
                             QBrush, QPainterPath)
import math


class KPICard(QWidget):
    """Professional KPI card widget with animated value display."""

    def __init__(self, title: str, value: str = "—", unit: str = "",
                  color: str = "#00D4FF", icon: str = "◆", parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.color = color
        self.icon_char = icon
        self._value = value
        self._pulse = 0
        self.setMinimumSize(160, 100)
        self.setMaximumHeight(120)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(color))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_timer.start(50)

    def _update_pulse(self):
        self._pulse = (self._pulse + 5) % 360
        self.update()

    def set_value(self, value: str):
        self._value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()

        # Background
        path = QPainterPath()
        path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), 10, 10)
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0, QColor("#12182E"))
        grad.setColorAt(1, QColor("#0A0E1A"))
        painter.fillPath(path, QBrush(grad))

        # Border with glow
        c = QColor(self.color)
        c.setAlpha(180)
        painter.setPen(QPen(c, 1.5))
        painter.drawPath(path)

        # Animated accent bar at top
        pulse_alpha = int(100 + 80 * math.sin(math.radians(self._pulse)))
        bar_color = QColor(self.color)
        bar_color.setAlpha(pulse_alpha)
        painter.fillRect(r.x() + 10, r.y() + 2, r.width() - 20, 3, bar_color)

        # Icon
        painter.setPen(QPen(QColor(self.color)))
        font = QFont("Arial", 14)
        painter.setFont(font)
        painter.drawText(r.x() + 12, r.y() + 30, self.icon_char)

        # Title
        painter.setPen(QPen(QColor("#8090B0")))
        font = QFont("Segoe UI", 8, QFont.Normal)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
        painter.setFont(font)
        painter.drawText(r.x() + 12, r.y() + 50, self.title.upper())

        # Value
        painter.setPen(QPen(QColor("#E8F0FF")))
        font = QFont("Segoe UI", 18, QFont.Bold)
        painter.setFont(font)
        painter.drawText(r.x() + 12, r.y() + 78, self._value)

        # Unit
        painter.setPen(QPen(QColor("#8090B0")))
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        val_width = painter.fontMetrics().horizontalAdvance(self._value)
        painter.drawText(r.x() + 12 + val_width + 5, r.y() + 78, self.unit)


class SignalStrengthBar(QWidget):
    """Animated signal strength indicator."""

    def __init__(self, n_bars=5, parent=None):
        super().__init__(parent)
        self.n_bars = n_bars
        self._level = 0.0  # 0..1
        self.setFixedSize(60, 30)
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self.update)
        self._anim_timer.start(100)

    def set_level(self, level: float):
        self._level = max(0.0, min(1.0, level))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        bar_w = max(1, w // self.n_bars - 2)

        for i in range(self.n_bars):
            bar_h = int(h * (i + 1) / self.n_bars)
            x = i * (bar_w + 2) + 2
            y = h - bar_h
            filled = (i + 1) / self.n_bars <= self._level
            if filled:
                frac = i / (self.n_bars - 1)
                r = int(0 + 255 * frac)
                g = int(212 - 80 * frac)
                b = int(255 - 167 * frac)
                color = QColor(r, g, b)
            else:
                color = QColor("#1A2A4A")
            painter.fillRect(x, y, bar_w, bar_h, color)


class StatusLED(QWidget):
    """Animated status LED indicator."""

    def __init__(self, color="#00FF88", parent=None):
        super().__init__(parent)
        self.color = color
        self._phase = 0
        self.setFixedSize(16, 16)
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(60)

    def _tick(self):
        self._phase = (self._phase + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        c = QColor(self.color)
        alpha = int(150 + 105 * math.sin(math.radians(self._phase)))
        c.setAlpha(alpha)
        painter.setBrush(QBrush(c))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 12, 12)


class SectionHeader(QWidget):
    """Section header with decorative line."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(10)

        lbl = QLabel(title.upper())
        lbl.setStyleSheet(
            "color: #00D4FF; font-size: 11px; font-weight: 700; "
            "letter-spacing: 2px; background: transparent;"
        )
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #1A2A4A;")
        layout.addWidget(lbl)
        layout.addWidget(line, 1)


class MatplotlibCanvas(QWidget):
    """Widget that displays a matplotlib figure as a pixmap."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("background: #0A0E1A;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

    def set_figure(self, fig):
        from utils.plotting import figure_to_pixmap
        if fig is None:
            return
        pm = figure_to_pixmap(fig)
        self._label.setPixmap(pm.scaled(
            self._label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        import matplotlib.pyplot as plt
        plt.close(fig)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._label.pixmap():
            self._label.setPixmap(self._label.pixmap().scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
