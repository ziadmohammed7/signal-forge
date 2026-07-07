"""
5G NR Extensions Tab: Numerology, Resource Blocks, Beamforming Visualization.
"""
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                  QComboBox, QPushButton, QFrame, QGroupBox,
                                  QFormLayout, QSpinBox, QSlider, QSplitter)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QPainterPath
from gui.widgets import SectionHeader, MatplotlibCanvas
import math
import utils.plotting as plt_utils
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# Numerology parameters per mu
NUMEROLOGY = {
    "μ=0 (15 kHz)": {"scs": 15e3, "slot_dur_ms": 1.0, "sym_per_slot": 14, "name": "LTE-like"},
    "μ=1 (30 kHz)": {"scs": 30e3, "slot_dur_ms": 0.5, "sym_per_slot": 14, "name": "5G NR FR1"},
    "μ=2 (60 kHz)": {"scs": 60e3, "slot_dur_ms": 0.25, "sym_per_slot": 14, "name": "5G NR FR2"},
}


class BeamformingWidget(QWidget):
    """Animated beamforming sector visualization."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self._phase = 0
        self._n_beams = 3
        self._active_beam = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(80)

    def set_beams(self, n_beams: int):
        self._n_beams = max(1, n_beams)
        self.update()

    def _tick(self):
        self._phase = (self._phase + 2) % 360
        self._active_beam = int(self._phase / 360 * self._n_beams)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        cx = r.width() // 2
        cy = r.height() // 2
        radius = min(cx, cy) - 20

        painter.fillRect(r, QColor("#0A0E1A"))

        # Grid circles
        for i in range(1, 5):
            c = QColor("#1A2A4A")
            painter.setPen(QPen(c, 0.8))
            painter.drawEllipse(cx - radius*i//4, cy - radius*i//4,
                                 radius*i//2, radius*i//2)

        # Draw each beam sector
        beam_angle = 360 / self._n_beams
        beam_colors = ["#00D4FF", "#7B2FFF", "#00FF88", "#FFB800", "#FF4560", "#FF88FF"]
        for i in range(self._n_beams):
            start_angle = i * beam_angle - beam_angle / 2 + 90
            is_active = (i == self._active_beam % self._n_beams)
            c = QColor(beam_colors[i % len(beam_colors)])
            if is_active:
                alpha = 120 + int(80 * math.sin(math.radians(self._phase * 4)))
                c.setAlpha(alpha)
                pen_width = 2.0
            else:
                c.setAlpha(30)
                pen_width = 0.8
            painter.setBrush(QBrush(c))
            painter.setPen(QPen(c, pen_width))
            path = QPainterPath()
            path.moveTo(cx, cy)
            path.arcTo(cx - radius, cy - radius, 2*radius, 2*radius,
                        start_angle, beam_angle)
            path.closeSubpath()
            painter.drawPath(path)

        # Center BS dot
        painter.setBrush(QBrush(QColor("#00D4FF")))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 7, cy - 7, 14, 14)

        # Active beam label
        painter.setPen(QPen(QColor("#E8F0FF")))
        font = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font)
        painter.drawText(r, Qt.AlignBottom | Qt.AlignHCenter,
                          f"Active Beam: {self._active_beam % self._n_beams + 1}/{self._n_beams}")


class FiveGTab(QWidget):
    """5G NR extensions and numerology simulation tab."""

    def __init__(self, simulation_state: dict, parent=None):
        super().__init__(parent)
        self.state = simulation_state
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(SectionHeader("5G NR Parameters & Visualization"))

        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel: numerology config
        left = QWidget()
        left.setMaximumWidth(340)
        left_vl = QVBoxLayout(left)
        left_vl.setContentsMargins(0, 0, 0, 0)
        left_vl.setSpacing(12)

        num_grp = QGroupBox("Numerology Selection (μ)")
        num_form = QFormLayout(num_grp)
        num_form.setSpacing(10)

        self.w_mu = QComboBox()
        self.w_mu.addItems(list(NUMEROLOGY.keys()))
        self.w_mu.currentTextChanged.connect(self._update_numerology_info)
        num_form.addRow("Numerology:", self.w_mu)

        self.lbl_scs = QLabel("15 kHz")
        self.lbl_scs.setStyleSheet("color: #00D4FF; font-weight: 700; background: transparent;")
        num_form.addRow("Subcarrier Spacing:", self.lbl_scs)

        self.lbl_slot = QLabel("1.0 ms")
        self.lbl_slot.setStyleSheet("color: #00D4FF; font-weight: 700; background: transparent;")
        num_form.addRow("Slot Duration:", self.lbl_slot)

        self.lbl_sym = QLabel("14")
        self.lbl_sym.setStyleSheet("color: #00D4FF; font-weight: 700; background: transparent;")
        num_form.addRow("Symbols/Slot:", self.lbl_sym)

        left_vl.addWidget(num_grp)

        rb_grp = QGroupBox("Resource Block Configuration")
        rb_form = QFormLayout(rb_grp)
        rb_form.setSpacing(10)

        self.w_n_rb = QSpinBox()
        self.w_n_rb.setRange(6, 132)
        self.w_n_rb.setValue(52)
        self.w_n_rb.setToolTip("Number of resource blocks (1 RB = 12 subcarriers)")
        rb_form.addRow("RB Count:", self.w_n_rb)

        self.lbl_bw = QLabel("—")
        self.lbl_bw.setStyleSheet("color: #00FF88; font-weight: 700; background: transparent;")
        rb_form.addRow("Total Bandwidth:", self.lbl_bw)

        self.lbl_cap = QLabel("—")
        self.lbl_cap.setStyleSheet("color: #FFB800; font-weight: 700; background: transparent;")
        rb_form.addRow("Peak Capacity:", self.lbl_cap)

        self.w_n_rb.valueChanged.connect(self._update_rb_info)
        left_vl.addWidget(rb_grp)

        beam_grp = QGroupBox("Beamforming")
        beam_form = QFormLayout(beam_grp)
        beam_form.setSpacing(10)

        self.w_n_beams = QComboBox()
        self.w_n_beams.addItems(["1 beam", "2 beams", "3 beams (standard)",
                                   "4 beams", "6 beams", "8 beams"])
        self.w_n_beams.setCurrentIndex(2)
        self.w_n_beams.currentIndexChanged.connect(self._update_beams)
        beam_form.addRow("Beam Count:", self.w_n_beams)

        self.lbl_gain = QLabel("—")
        self.lbl_gain.setStyleSheet("color: #7B2FFF; font-weight: 700; background: transparent;")
        beam_form.addRow("Array Gain:", self.lbl_gain)

        left_vl.addWidget(beam_grp)

        btn_plot = QPushButton("📊  Generate 5G Plots")
        btn_plot.setObjectName("primary")
        btn_plot.setMinimumHeight(36)
        btn_plot.clicked.connect(self._plot_all)
        left_vl.addWidget(btn_plot)

        left_vl.addStretch()
        main_splitter.addWidget(left)

        # Right panel: beamforming + plots
        right = QWidget()
        right_vl = QVBoxLayout(right)
        right_vl.setContentsMargins(0, 0, 0, 0)
        right_vl.setSpacing(10)

        # Beamforming visualizer
        self.beam_widget = BeamformingWidget()
        self.beam_widget.setMinimumHeight(240)
        right_vl.addWidget(self.beam_widget)

        # RB grid plot
        self.rb_canvas = MatplotlibCanvas()
        self.rb_canvas.setMinimumHeight(200)
        right_vl.addWidget(self.rb_canvas)

        main_splitter.addWidget(right)
        main_splitter.setSizes([320, 600])
        layout.addWidget(main_splitter, 1)

        # Initial update
        self._update_numerology_info()
        self._update_rb_info()
        self._plot_rb_grid()

    def _update_numerology_info(self):
        key = self.w_mu.currentText()
        nu = NUMEROLOGY[key]
        self.lbl_scs.setText(f"{nu['scs']/1e3:.0f} kHz")
        self.lbl_slot.setText(f"{nu['slot_dur_ms']} ms")
        self.lbl_sym.setText(str(nu["sym_per_slot"]))
        self._update_rb_info()

    def _update_rb_info(self):
        key = self.w_mu.currentText()
        nu = NUMEROLOGY[key]
        n_rb = self.w_n_rb.value()
        bw = n_rb * 12 * nu["scs"] / 1e6
        self.lbl_bw.setText(f"{bw:.2f} MHz")
        # Peak: 64QAM, 4/4 MIMO (simplified)
        cap = bw * 1e6 * np.log2(1 + 10**(25/10)) / 1e9
        self.lbl_cap.setText(f"~{cap:.2f} Gbps (64QAM est.)")

    def _update_beams(self):
        idx = self.w_n_beams.currentIndex()
        n_beams = [1, 2, 3, 4, 6, 8][idx]
        self.beam_widget.set_beams(n_beams)
        gain = 10 * np.log10(n_beams * 4)  # rough array gain
        self.lbl_gain.setText(f"~{gain:.1f} dBi")

    def _plot_all(self):
        self._plot_rb_grid()

    def _plot_rb_grid(self):
        """Plot resource block time-frequency grid."""
        key = self.w_mu.currentText()
        nu = NUMEROLOGY[key]
        n_rb = min(self.w_n_rb.value(), 50)
        n_slots = 10

        fig, (ax,) = plt_utils.dark_figure(figsize=(8, 4))
        ax.set_facecolor("#0A0E1A")

        colors_map = plt.cm.get_cmap("Set1", 6)
        ue_assignments = np.random.randint(0, 5, (n_rb, n_slots))
        ue_colors = ["#00D4FF", "#7B2FFF", "#00FF88", "#FFB800", "#FF4560"]
        ue_labels = [f"UE {i+1}" for i in range(5)]

        for rb in range(n_rb):
            for slot in range(n_slots):
                ue = ue_assignments[rb, slot]
                c = QColor(ue_colors[ue])
                rect_color = ue_colors[ue]
                ax.add_patch(plt.Rectangle((slot, rb), 0.95, 0.95,
                                            color=rect_color, alpha=0.75))

        ax.set_xlim(0, n_slots)
        ax.set_ylim(0, n_rb)
        ax.set_xlabel("Slot (Time)", color=plt_utils.TEXT_COLOR)
        ax.set_ylabel("Resource Block (Freq)", color=plt_utils.TEXT_COLOR)
        scs_khz = nu["scs"] / 1e3
        ax.set_title(
            f"Resource Grid  |  SCS={scs_khz:.0f} kHz  |  {n_rb} RBs  |  {n_slots} Slots",
            color=plt_utils.TEXT_COLOR, fontsize=10, fontweight='bold'
        )

        patches = [mpatches.Patch(color=ue_colors[i], label=ue_labels[i]) for i in range(5)]
        ax.legend(handles=patches, loc='upper right',
                   facecolor="#0F1629", edgecolor="#1A2A4A",
                   labelcolor=plt_utils.TEXT_COLOR, fontsize=8)
        fig.tight_layout()
        self.rb_canvas.set_figure(fig)
