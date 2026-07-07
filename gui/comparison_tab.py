"""
Comparison Tab: Multi-modulation BER comparison.
"""
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                  QListWidget, QListWidgetItem, QPushButton,
                                  QFrame, QComboBox, QProgressBar, QCheckBox,
                                  QGroupBox, QFormLayout)
from PySide6.QtCore import Qt, QThread, Signal
from gui.widgets import SectionHeader, MatplotlibCanvas
from core.modulation import compute_ber
import utils.plotting as plt_utils
import numpy as np


class MultiWorker(QThread):
    progress = Signal(str)
    finished = Signal(dict)

    def __init__(self, schemes, channel, snr_range):
        super().__init__()
        self.schemes = schemes
        self.channel = channel
        self.snr_range = snr_range

    def run(self):
        results = {}
        for scheme in self.schemes:
            self.progress.emit(f"Computing {scheme}...")
            ber = compute_ber(self.snr_range, scheme, self.channel, n_bits=20000)
            results[scheme] = ber
        self.finished.emit(results)


class ComparisonTab(QWidget):
    """Side-by-side modulation scheme comparison."""

    def __init__(self, simulation_state: dict, parent=None):
        super().__init__(parent)
        self.state = simulation_state
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Left panel: selection
        left_panel = QFrame()
        left_panel.setStyleSheet(
            "background: #12182E; border: 1px solid #1A2A4A; border-radius: 8px;"
        )
        left_panel.setMaximumWidth(260)
        left_vl = QVBoxLayout(left_panel)
        left_vl.setContentsMargins(14, 14, 14, 14)
        left_vl.setSpacing(10)

        left_vl.addWidget(SectionHeader("Modulation Select"))

        schemes_grp = QGroupBox("Select Schemes")
        schemes_vl = QVBoxLayout(schemes_grp)
        self._checkboxes = {}
        for scheme in ["BPSK", "QPSK", "8PSK", "16QAM"]:
            cb = QCheckBox(scheme)
            cb.setChecked(True)
            schemes_vl.addWidget(cb)
            self._checkboxes[scheme] = cb
        left_vl.addWidget(schemes_grp)

        ch_grp = QGroupBox("Channel")
        ch_vl = QVBoxLayout(ch_grp)
        self.w_channel = QComboBox()
        self.w_channel.addItems(["AWGN", "Rayleigh", "Rician"])
        ch_vl.addWidget(self.w_channel)
        left_vl.addWidget(ch_grp)

        snr_grp = QGroupBox("SNR Range")
        snr_vl = QVBoxLayout(snr_grp)
        self.w_snr_max = QComboBox()
        self.w_snr_max.addItems(["20 dB", "25 dB", "30 dB", "35 dB", "40 dB"])
        self.w_snr_max.setCurrentText("30 dB")
        snr_vl.addWidget(self.w_snr_max)
        left_vl.addWidget(snr_grp)

        self.btn_compare = QPushButton("▶  Run Comparison")
        self.btn_compare.setObjectName("primary")
        self.btn_compare.setMinimumHeight(36)
        self.btn_compare.clicked.connect(self._run)
        left_vl.addWidget(self.btn_compare)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        left_vl.addWidget(self.progress_bar)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #8090B0; font-size: 9px; background: transparent;")
        self.status_lbl.setWordWrap(True)
        left_vl.addWidget(self.status_lbl)

        # Stats box
        stats_grp = QGroupBox("Statistics")
        stats_vl = QVBoxLayout(stats_grp)
        self.stats_lbl = QLabel("Run comparison to see results.")
        self.stats_lbl.setWordWrap(True)
        self.stats_lbl.setStyleSheet("color: #C8D6F0; font-size: 10px; background: transparent;")
        stats_vl.addWidget(self.stats_lbl)
        left_vl.addWidget(stats_grp)

        left_vl.addStretch()
        layout.addWidget(left_panel)

        # Right: plot
        right_widget = QWidget()
        right_vl = QVBoxLayout(right_widget)
        right_vl.setContentsMargins(0, 0, 0, 0)
        right_vl.addWidget(SectionHeader("BER Comparison Plot"))
        self.ber_canvas = MatplotlibCanvas()
        right_vl.addWidget(self.ber_canvas, 1)
        layout.addWidget(right_widget, 1)

    def _run(self):
        selected = [s for s, cb in self._checkboxes.items() if cb.isChecked()]
        if not selected:
            self.status_lbl.setText("Select at least one scheme.")
            return
        if self._worker and self._worker.isRunning():
            return

        snr_max = int(self.w_snr_max.currentText().split()[0])
        snr_range = np.arange(-5, snr_max + 1, 1)

        self.btn_compare.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_lbl.setText("Computing...")

        self._worker = MultiWorker(selected, self.w_channel.currentText(), snr_range)
        self._worker.progress.connect(self.status_lbl.setText)
        self._worker.finished.connect(lambda r: self._on_finished(r, snr_range))
        self._worker.start()

    def _on_finished(self, results: dict, snr_range):
        self.btn_compare.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_lbl.setText("Done.")

        fig = plt_utils.plot_ber_vs_snr(
            snr_range, results,
            title=f"BER vs SNR — {self.w_channel.currentText()} Channel"
        )
        self.ber_canvas.set_figure(fig)

        # Stats
        stat_lines = []
        for scheme, ber in results.items():
            # SNR at BER=1e-3
            try:
                idx = next(i for i, b in enumerate(ber) if b <= 1e-3)
                snr_req = snr_range[idx]
                stat_lines.append(f"{scheme}: SNR@BER=10⁻³ ≈ {snr_req} dB")
            except StopIteration:
                stat_lines.append(f"{scheme}: BER > 10⁻³ in range")
        self.stats_lbl.setText("\n".join(stat_lines))
