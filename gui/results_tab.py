"""
Results Tab: BER vs SNR, Constellation, FFT, Throughput
"""
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                  QComboBox, QPushButton, QFrame, QTabWidget,
                                  QFileDialog, QSlider, QSizePolicy, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal
from gui.widgets import SectionHeader, MatplotlibCanvas
from core.modulation import compute_ber
from core.sinr import estimate_throughput_mbps
import utils.plotting as plt_utils
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class BERWorker(QThread):
    progress = Signal(int)
    finished = Signal(dict)

    def __init__(self, scheme, channel, snr_range):
        super().__init__()
        self.scheme = scheme
        self.channel = channel
        self.snr_range = snr_range

    def run(self):
        ber = compute_ber(self.snr_range, self.scheme, self.channel, n_bits=20000)
        self.finished.emit({"scheme": self.scheme, "ber": ber})


class ResultsTab(QWidget):
    """Results and plots tab."""

    def __init__(self, simulation_state: dict, parent=None):
        super().__init__(parent)
        self.state = simulation_state
        self._ber_data = {}
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Control bar
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet(
            "background: #12182E; border: 1px solid #1A2A4A; border-radius: 8px; padding: 10px;"
        )
        ctrl = QHBoxLayout(ctrl_frame)
        ctrl.setSpacing(12)

        ctrl.addWidget(QLabel("Modulation:"))
        self.w_mod = QComboBox()
        self.w_mod.addItems(["BPSK", "QPSK", "8PSK", "16QAM"])
        self.w_mod.setCurrentText("16QAM")
        ctrl.addWidget(self.w_mod)

        ctrl.addWidget(QLabel("Channel:"))
        self.w_ch = QComboBox()
        self.w_ch.addItems(["AWGN", "Rayleigh", "Rician"])
        ctrl.addWidget(self.w_ch)

        ctrl.addWidget(QLabel("SNR Max:"))
        self.w_snr_max = QSlider(Qt.Horizontal)
        self.w_snr_max.setRange(15, 50)
        self.w_snr_max.setValue(30)
        self.w_snr_max.setFixedWidth(100)
        self.w_snr_lbl = QLabel("30 dB")
        self.w_snr_lbl.setStyleSheet("color: #00D4FF; font-weight: 700; background: transparent; min-width:40px;")
        self.w_snr_max.valueChanged.connect(lambda v: self.w_snr_lbl.setText(f"{v} dB"))
        ctrl.addWidget(self.w_snr_max)
        ctrl.addWidget(self.w_snr_lbl)

        ctrl.addStretch()
        self.btn_compute = QPushButton("▶  Compute BER")
        self.btn_compute.setObjectName("primary")
        self.btn_compute.setMinimumHeight(34)
        self.btn_compute.clicked.connect(self._compute_ber)
        ctrl.addWidget(self.btn_compute)

        self.btn_export = QPushButton("💾  Export PNG")
        self.btn_export.setMinimumHeight(34)
        self.btn_export.clicked.connect(self._export)
        ctrl.addWidget(self.btn_export)

        layout.addWidget(ctrl_frame)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)
        layout.addWidget(self.progress)

        # Sub-tabs
        sub_tabs = QTabWidget()
        sub_tabs.setStyleSheet("QTabBar::tab { min-width: 80px; padding: 6px 14px; font-size: 10px; }")
        layout.addWidget(sub_tabs, 1)

        # BER plot
        ber_widget = QWidget()
        ber_vl = QVBoxLayout(ber_widget)
        ber_vl.setContentsMargins(4, 4, 4, 4)
        self.ber_canvas = MatplotlibCanvas()
        ber_vl.addWidget(self.ber_canvas)
        sub_tabs.addTab(ber_widget, "📉 BER vs SNR")

        # Constellation
        const_widget = QWidget()
        const_vl = QVBoxLayout(const_widget)
        const_vl.setContentsMargins(4, 4, 4, 4)
        self.const_canvas = MatplotlibCanvas()
        const_vl.addWidget(self.const_canvas)
        sub_tabs.addTab(const_widget, "🔵 Constellation")

        # FFT
        fft_widget = QWidget()
        fft_vl = QVBoxLayout(fft_widget)
        fft_vl.setContentsMargins(4, 4, 4, 4)
        self.fft_canvas = MatplotlibCanvas()
        fft_vl.addWidget(self.fft_canvas)
        sub_tabs.addTab(fft_widget, "📊 FFT Spectrum")

        # Throughput
        tp_widget = QWidget()
        tp_vl = QVBoxLayout(tp_widget)
        tp_vl.setContentsMargins(4, 4, 4, 4)
        self.tp_canvas = MatplotlibCanvas()
        tp_vl.addWidget(self.tp_canvas)
        sub_tabs.addTab(tp_widget, "⚡ Throughput")

        self._plot_throughput()
        self._current_fig = None

    def _compute_ber(self):
        if self._worker and self._worker.isRunning():
            return
        self.btn_compute.setEnabled(False)
        self.progress.setVisible(True)
        snr_max = self.w_snr_max.value()
        snr_range = np.arange(-5, snr_max + 1, 1)
        self._worker = BERWorker(
            self.w_mod.currentText(),
            self.w_ch.currentText(),
            snr_range
        )
        self._worker.finished.connect(self._on_ber)
        self._worker.start()
        self._snr_range = snr_range

    def _on_ber(self, result: dict):
        self.btn_compute.setEnabled(True)
        self.progress.setVisible(False)
        key = f"{result['scheme']} ({self.w_ch.currentText()})"
        self._ber_data[key] = result["ber"]

        fig = plt_utils.plot_ber_vs_snr(self._snr_range, self._ber_data)
        self.ber_canvas.set_figure(fig)
        self._current_fig = plt_utils.plot_ber_vs_snr(self._snr_range, self._ber_data)

        # Also update constellation
        from core.modulation import generate_bits, modulate, get_constellation
        from core.channel_models import add_noise
        bits = generate_bits(4000)
        syms = modulate(bits, self.w_mod.currentText())
        rx = add_noise(syms, 12)
        ideal = get_constellation(self.w_mod.currentText())
        const_fig = plt_utils.plot_constellation(rx[:500], self.w_mod.currentText(), ideal)
        self.const_canvas.set_figure(const_fig)

        # FFT
        fft_fig = plt_utils.plot_fft_spectrum(syms, title=f"{self.w_mod.currentText()} TX Spectrum")
        self.fft_canvas.set_figure(fft_fig)

    def _plot_throughput(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        snr_range = np.arange(-5, 35, 1)
        bw = 10e6  # 10 MHz
        tp = [estimate_throughput_mbps(s, bw) for s in snr_range]
        fig, (ax,) = plt_utils.dark_figure(figsize=(8, 4))
        ax.plot(snr_range, tp, color=plt_utils.ACCENT, linewidth=2)
        ax.fill_between(snr_range, tp, alpha=0.15, color=plt_utils.ACCENT)
        ax.set_xlabel("SNR (dB)", color=plt_utils.TEXT_COLOR)
        ax.set_ylabel("Throughput (Mbps)", color=plt_utils.TEXT_COLOR)
        ax.set_title("Shannon Capacity (10 MHz BW)", color=plt_utils.TEXT_COLOR,
                      fontsize=11, fontweight='bold')
        fig.tight_layout()
        self.tp_canvas.set_figure(fig)

    def _export(self):
        if self._current_fig is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Plot", "ber_plot.png", "PNG (*.png)")
        if path:
            self._current_fig.savefig(path, dpi=150, bbox_inches='tight',
                                       facecolor=self._current_fig.get_facecolor())
