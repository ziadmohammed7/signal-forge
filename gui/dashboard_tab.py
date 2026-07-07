"""
Dashboard Tab - Professional overview with KPI cards and system diagram.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                  QGridLayout, QFrame, QSizePolicy, QScrollArea)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QLinearGradient, QColor, QPainter, QBrush, QPen, QPainterPath

from gui.widgets import KPICard, StatusLED, SectionHeader, SignalStrengthBar
import math


class HeroWidget(QWidget):
    """Animated hero banner for the dashboard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(160)
        self.setMaximumHeight(170)
        self._phase = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)

    def _tick(self):
        self._phase += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()

        # Gradient background
        grad = QLinearGradient(0, 0, r.width(), r.height())
        grad.setColorAt(0, QColor("#050810"))
        grad.setColorAt(0.5, QColor("#0A1428"))
        grad.setColorAt(1, QColor("#060C1C"))
        painter.fillRect(r, QBrush(grad))

        # Animated wave lines
        for j in range(5):
            p = self._phase * 0.02 + j * 0.7
            amplitude = 18 + j * 6
            y_offset = r.height() // 2 + j * 12 - 30
            path = QPainterPath()
            path.moveTo(0, y_offset)
            for x in range(0, r.width() + 10, 5):
                y = y_offset + amplitude * math.sin(x * 0.012 + p)
                path.lineTo(x, y)
            alpha = max(20, 80 - j * 12)
            colors = ["#00D4FF", "#7B2FFF", "#00FF88", "#FFB800", "#00D4FF"]
            c = QColor(colors[j % len(colors)])
            c.setAlpha(alpha)
            painter.setPen(QPen(c, 1.2))
            painter.drawPath(path)

        # Grid dots
        for gx in range(0, r.width(), 40):
            for gy in range(0, r.height(), 40):
                c2 = QColor("#00D4FF")
                c2.setAlpha(25)
                painter.fillRect(gx, gy, 2, 2, c2)

        # Title text
        painter.setPen(QPen(QColor("#E8F0FF")))
        font = QFont("Segoe UI", 22, QFont.Bold)
        painter.setFont(font)
        painter.drawText(r.adjusted(30, 0, 0, -50), Qt.AlignVCenter | Qt.AlignLeft,
                          "Mobile Communication\nSystem Simulator")

        # Subtitle
        painter.setPen(QPen(QColor("#8090B0")))
        font = QFont("Segoe UI", 10)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2.5)
        painter.setFont(font)
        painter.drawText(r.adjusted(32, 90, 0, 0), Qt.AlignTop | Qt.AlignLeft,
                          "REAL-TIME CELLULAR NETWORK ANALYSIS PLATFORM")

        # Accent line
        accent_c = QColor("#00D4FF")
        accent_c.setAlpha(200)
        painter.fillRect(28, r.height() - 3, 120, 3, accent_c)

        # Version badge
        painter.setPen(QPen(QColor("#00D4FF")))
        painter.setBrush(QBrush(QColor("#0F1629")))
        painter.drawRoundedRect(r.width() - 90, 20, 70, 22, 11, 11)
        painter.setPen(QPen(QColor("#00D4FF")))
        font = QFont("Segoe UI", 8, QFont.Bold)
        painter.setFont(font)
        painter.drawText(r.width() - 90, 20, 70, 22, Qt.AlignCenter, "v2.0 LTE/5G")

        # Signal bars top right
        for i in range(5):
            bh = (i + 1) * 6
            bx = r.width() - 90 - 50 + i * 9
            by = r.height() - bh - 8
            frac = (i + 1) / 5
            c3 = QColor(int(0 + 255*frac), int(212 - 80*frac), 255)
            c3.setAlpha(200)
            painter.fillRect(bx, by, 6, bh, c3)


class SystemDiagramWidget(QWidget):
    """Animated system block diagram."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self._phase = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(60)

        self.blocks = [
            ("BIT GEN", "#00D4FF"),
            ("MODULATOR", "#7B2FFF"),
            ("CHANNEL", "#FFB800"),
            ("DEMOD", "#00FF88"),
            ("BER CALC", "#FF4560"),
        ]

    def _tick(self):
        self._phase = (self._phase + 3) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        painter.fillRect(r, QColor("#0A0E1A"))

        n = len(self.blocks)
        block_w = 90
        block_h = 44
        spacing = (r.width() - n * block_w) / (n + 1)
        y_center = r.height() // 2

        for i, (name, color) in enumerate(self.blocks):
            x = spacing + i * (block_w + spacing)
            y = y_center - block_h // 2

            # Draw arrow between blocks
            if i > 0:
                arrow_x = x - spacing
                pulse = int(100 + 80 * math.sin(math.radians(self._phase - i * 40)))
                ac = QColor(color)
                ac.setAlpha(pulse)
                painter.setPen(QPen(ac, 2))
                painter.drawLine(int(arrow_x - block_w // 2 + block_w),
                                  y_center,
                                  int(x), y_center)
                # arrowhead
                ax = int(x)
                painter.drawLine(ax, y_center, ax - 8, y_center - 5)
                painter.drawLine(ax, y_center, ax - 8, y_center + 5)

            # Block background
            bc = QColor(color)
            bc.setAlpha(25)
            painter.fillRect(int(x), int(y), block_w, block_h, bc)
            border_c = QColor(color)
            border_c.setAlpha(200)
            painter.setPen(QPen(border_c, 1.5))
            painter.drawRoundedRect(int(x), int(y), block_w, block_h, 6, 6)

            # Text
            painter.setPen(QPen(QColor(color)))
            font = QFont("Segoe UI", 8, QFont.Bold)
            painter.setFont(font)
            painter.drawText(int(x), int(y), block_w, block_h,
                              Qt.AlignCenter, name)


class DashboardTab(QWidget):
    """Main dashboard overview tab."""

    def __init__(self, simulation_state: dict, parent=None):
        super().__init__(parent)
        self.state = simulation_state
        self._setup_ui()
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._update_kpis)
        self._refresh_timer.start(1000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        layout.addWidget(scroll)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(18, 18, 18, 18)
        vbox.setSpacing(16)
        scroll.setWidget(container)

        # Hero
        hero = HeroWidget()
        vbox.addWidget(hero)

        # Status row
        status_row = QHBoxLayout()
        self._status_led = StatusLED("#00FF88")
        self._status_label = QLabel("SIMULATION READY")
        self._status_label.setStyleSheet(
            "color: #00FF88; font-size: 10px; font-weight: 700; "
            "letter-spacing: 2px; background: transparent;"
        )
        status_row.addWidget(self._status_led)
        status_row.addWidget(self._status_label)
        status_row.addStretch()

        self._time_label = QLabel("Sim Time: 0.0 s")
        self._time_label.setStyleSheet("color: #8090B0; font-size: 10px; background: transparent;")
        status_row.addWidget(self._time_label)
        vbox.addLayout(status_row)

        # KPI Cards
        vbox.addWidget(SectionHeader("Key Performance Indicators"))
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(12)

        self.kpi_sinr = KPICard("Avg SINR", "—", "dB", "#00D4FF", "📶")
        self.kpi_handoff = KPICard("Handoffs", "0", "", "#7B2FFF", "🔄")
        self.kpi_users = KPICard("Active Users", "0", "UEs", "#00FF88", "👥")
        self.kpi_load = KPICard("Cell Load", "—", "%", "#FFB800", "📊")
        self.kpi_throughput = KPICard("Throughput", "—", "Mbps", "#FF4560", "⚡")
        self.kpi_ber = KPICard("Avg BER", "—", "", "#00AAFF", "📉")

        cards = [self.kpi_sinr, self.kpi_handoff, self.kpi_users,
                  self.kpi_load, self.kpi_throughput, self.kpi_ber]
        for i, card in enumerate(cards):
            kpi_grid.addWidget(card, i // 3, i % 3)

        vbox.addLayout(kpi_grid)

        # System diagram
        vbox.addWidget(SectionHeader("Digital Communication Chain"))
        diag = SystemDiagramWidget()
        diag.setStyleSheet("border-radius: 8px;")
        vbox.addWidget(diag)

        # Info grid
        vbox.addWidget(SectionHeader("System Overview"))
        info_grid = QGridLayout()
        info_grid.setSpacing(10)

        info_items = [
            ("Network Type", "LTE / 5G NR", "#00D4FF"),
            ("Cell Layout", "Hexagonal Grid", "#7B2FFF"),
            ("Channel Model", "Rayleigh/Rician/AWGN", "#00FF88"),
            ("Scheduler", "Proportional Fair", "#FFB800"),
            ("Handover Algorithm", "A3 Event-Based", "#FF4560"),
            ("Mobility Model", "Random Waypoint", "#00AAFF"),
        ]
        for i, (label, value, color) in enumerate(info_items):
            frame = QFrame()
            frame.setStyleSheet(
                f"background: #12182E; border: 1px solid #1A2A4A; border-radius: 8px; padding: 8px;"
            )
            fl = QVBoxLayout(frame)
            fl.setSpacing(4)
            lbl = QLabel(label.upper())
            lbl.setStyleSheet(f"color: {color}; font-size: 8px; font-weight: 700; "
                               f"letter-spacing: 1.5px; background: transparent;")
            val = QLabel(value)
            val.setStyleSheet("color: #E8F0FF; font-size: 12px; font-weight: 600; background: transparent;")
            fl.addWidget(lbl)
            fl.addWidget(val)
            info_grid.addWidget(frame, i // 3, i % 3)

        vbox.addLayout(info_grid)
        vbox.addStretch()

    def _update_kpis(self):
        kpis = self.state.get("kpis", {})
        avg_sinr = kpis.get("avg_sinr", None)
        self.kpi_sinr.set_value(f"{avg_sinr:.1f}" if avg_sinr is not None else "—")
        self.kpi_handoff.set_value(str(kpis.get("handoff_count", 0)))
        self.kpi_users.set_value(str(kpis.get("active_users", 0)))
        cell_load = kpis.get("cell_load", None)
        self.kpi_load.set_value(f"{cell_load*100:.0f}" if cell_load is not None else "—")
        tp = kpis.get("avg_throughput", None)
        self.kpi_throughput.set_value(f"{tp:.2f}" if tp is not None else "—")
        ber = kpis.get("avg_ber", None)
        self.kpi_ber.set_value(f"{ber:.2e}" if ber is not None else "—")

        running = self.state.get("running", False)
        sim_time = self.state.get("sim_time", 0.0)
        self._time_label.setText(f"Sim Time: {sim_time:.1f} s")
        if running:
            self._status_label.setText("SIMULATION RUNNING")
            self._status_label.setStyleSheet(
                "color: #00D4FF; font-size: 10px; font-weight: 700; "
                "letter-spacing: 2px; background: transparent;"
            )
            self._status_led.color = "#00D4FF"
        else:
            self._status_label.setText("SIMULATION IDLE")
            self._status_label.setStyleSheet(
                "color: #00FF88; font-size: 10px; font-weight: 700; "
                "letter-spacing: 2px; background: transparent;"
            )
            self._status_led.color = "#00FF88"
