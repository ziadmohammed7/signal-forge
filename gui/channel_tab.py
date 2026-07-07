"""
Channel Simulation Tab: Real-time signal degradation visualization.
"""
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                  QComboBox, QPushButton, QFrame, QSlider,
                                  QGroupBox, QFormLayout, QSplitter, QDoubleSpinBox)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from gui.widgets import SectionHeader, MatplotlibCanvas
from core.modulation import generate_bits, modulate, get_constellation
from core.channel_models import add_noise, apply_rayleigh, apply_rician
import utils.plotting as plt_utils
import numpy as np


class ChannelWorker(QThread):
    ready = Signal(dict)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        p = self.params
        scheme = p.get("modulation", "QPSK")
        channel = p.get("channel", "AWGN")
        snr_db = p.get("snr_db", 10.0)
        n = 3000

        bits = generate_bits(n)
        tx = modulate(bits, scheme)

        if channel == "AWGN":
            rx = add_noise(tx, snr_db)
        elif channel == "Rayleigh":
            rx = apply_rayleigh(tx, snr_db)
        else:
            rx = apply_rician(tx, snr_db)

        ideal = get_constellation(scheme)
        waveform_fig = plt_utils.plot_waveform(tx, "TX Waveform (Clean)", 200)
        rx_waveform_fig = plt_utils.plot_waveform(rx, "RX Waveform (After Channel)", 200)
        const_fig = plt_utils.plot_constellation(rx[:600], scheme, ideal)
        fft_fig = plt_utils.plot_fft_spectrum(rx, title="RX Spectrum (Post-Channel)")

        # Compute noise envelope
        noise = rx - tx[:len(rx)]
        noise_fig = plt_utils.plot_waveform(noise, "Noise Envelope", 200)

        self.ready.emit({
            "waveform_fig": waveform_fig,
            "rx_waveform_fig": rx_waveform_fig,
            "const_fig": const_fig,
            "fft_fig": fft_fig,
            "noise_fig": noise_fig,
            "snr_db": snr_db,
            "channel": channel,
            "scheme": scheme,
        })


class ChannelTab(QWidget):
    """Interactive channel simulation and visualization."""

    def __init__(self, simulation_state: dict, parent=None):
        super().__init__(parent)
        self.state = simulation_state
        self._worker = None
        self._auto_timer = QTimer()
        self._auto_timer.timeout.connect(self._run)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Controls
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet(
            "background: #12182E; border: 1px solid #1A2A4A; border-radius: 8px; padding: 10px;"
        )
        ctrl = QHBoxLayout(ctrl_frame)
        ctrl.setSpacing(14)

        ctrl.addWidget(QLabel("Channel:"))
        self.w_channel = QComboBox()
        self.w_channel.addItems(["AWGN", "Rayleigh", "Rician"])
        self.w_channel.setToolTip("Select propagation channel model")
        ctrl.addWidget(self.w_channel)

        ctrl.addWidget(QLabel("Modulation:"))
        self.w_mod = QComboBox()
        self.w_mod.addItems(["BPSK", "QPSK", "8PSK", "16QAM"])
        self.w_mod.setCurrentText("QPSK")
        ctrl.addWidget(self.w_mod)

        ctrl.addWidget(QLabel("SNR:"))
        self.w_snr_slider = QSlider(Qt.Horizontal)
        self.w_snr_slider.setRange(-5, 30)
        self.w_snr_slider.setValue(10)
        self.w_snr_slider.setFixedWidth(180)
        self.w_snr_slider.setToolTip("Adjust SNR to observe signal degradation")
        self.w_snr_lbl = QLabel("10 dB")
        self.w_snr_lbl.setStyleSheet(
            "color: #00D4FF; font-weight: 700; min-width: 45px; background: transparent;"
        )
        self.w_snr_slider.valueChanged.connect(self._on_snr_change)
        ctrl.addWidget(self.w_snr_slider)
        ctrl.addWidget(self.w_snr_lbl)

        ctrl.addStretch()

        self.btn_auto = QPushButton("⏵  Auto Update")
        self.btn_auto.setCheckable(True)
        self.btn_auto.setMinimumHeight(34)
        self.btn_auto.toggled.connect(self._toggle_auto)
        ctrl.addWidget(self.btn_auto)

        self.btn_update = QPushButton("↺  Update")
        self.btn_update.setObjectName("primary")
        self.btn_update.setMinimumHeight(34)
        self.btn_update.clicked.connect(self._run)
        ctrl.addWidget(self.btn_update)

        layout.addWidget(ctrl_frame)

        # Channel info bar
        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background: #0F1629; border: 1px solid #1A2A4A; border-radius: 6px; padding: 8px 14px;"
        )
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(30)

        self._make_info_label(info_layout, "CHANNEL", "AWGN", "#00D4FF", "lbl_channel")
        self._make_info_label(info_layout, "SNR", "10 dB", "#7B2FFF", "lbl_snr")
        self._make_info_label(info_layout, "MODULATION", "QPSK", "#00FF88", "lbl_mod")
        self._make_info_label(info_layout, "NOISE POWER", "—", "#FFB800", "lbl_noise")
        info_layout.addStretch()
        layout.addWidget(info_frame)

        # Plot grid
        splitter_v = QSplitter(Qt.Vertical)
        splitter_h1 = QSplitter(Qt.Horizontal)
        splitter_h2 = QSplitter(Qt.Horizontal)

        # Row 1: TX waveform | RX waveform
        tx_widget = self._plot_widget("TX Waveform (Clean Signal)")
        self.tx_canvas = tx_widget[1]
        rx_widget = self._plot_widget("RX Waveform (After Channel)")
        self.rx_canvas = rx_widget[1]
        splitter_h1.addWidget(tx_widget[0])
        splitter_h1.addWidget(rx_widget[0])

        # Row 2: Constellation | FFT | Noise
        const_widget = self._plot_widget("Constellation (RX)")
        self.const_canvas = const_widget[1]
        fft_widget = self._plot_widget("FFT Spectrum")
        self.fft_canvas = fft_widget[1]
        noise_widget = self._plot_widget("Noise Envelope")
        self.noise_canvas = noise_widget[1]
        splitter_h2.addWidget(const_widget[0])
        splitter_h2.addWidget(fft_widget[0])
        splitter_h2.addWidget(noise_widget[0])

        splitter_v.addWidget(splitter_h1)
        splitter_v.addWidget(splitter_h2)
        splitter_v.setSizes([300, 300])
        layout.addWidget(splitter_v, 1)

    def _plot_widget(self, title: str):
        w = QFrame()
        w.setStyleSheet("background: #0A0E1A; border: 1px solid #1A2A4A; border-radius: 6px;")
        vl = QVBoxLayout(w)
        vl.setContentsMargins(6, 6, 6, 6)
        lbl = QLabel(title)
        lbl.setStyleSheet("color: #8090B0; font-size: 9px; font-weight: 600; "
                           "letter-spacing: 1px; background: transparent;")
        canvas = MatplotlibCanvas()
        vl.addWidget(lbl)
        vl.addWidget(canvas)
        return w, canvas

    def _make_info_label(self, layout, title, value, color, attr):
        frame = QFrame()
        frame.setStyleSheet("background: transparent;")
        vl = QVBoxLayout(frame)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet(f"color: {color}; font-size: 8px; font-weight: 700; "
                         f"letter-spacing: 1.5px; background: transparent;")
        v = QLabel(value)
        v.setStyleSheet("color: #E8F0FF; font-size: 13px; font-weight: 600; background: transparent;")
        setattr(self, attr, v)
        vl.addWidget(t)
        vl.addWidget(v)
        layout.addWidget(frame)

    def _on_snr_change(self, val):
        self.w_snr_lbl.setText(f"{val} dB")
        self.lbl_snr.setText(f"{val} dB")
        if self.btn_auto.isChecked():
            self._run()

    def _toggle_auto(self, checked):
        if checked:
            self.btn_auto.setText("⏸  Auto ON")
            self._auto_timer.start(800)
        else:
            self.btn_auto.setText("⏵  Auto Update")
            self._auto_timer.stop()

    def _run(self):
        if self._worker and self._worker.isRunning():
            return
        params = {
            "modulation": self.w_mod.currentText(),
            "channel": self.w_channel.currentText(),
            "snr_db": float(self.w_snr_slider.value()),
        }
        self.lbl_channel.setText(params["channel"])
        self.lbl_mod.setText(params["modulation"])
        self._worker = ChannelWorker(params)
        self._worker.ready.connect(self._on_ready)
        self._worker.start()

    def _on_ready(self, result: dict):
        self.tx_canvas.set_figure(result["waveform_fig"])
        self.rx_canvas.set_figure(result["rx_waveform_fig"])
        self.const_canvas.set_figure(result["const_fig"])
        self.fft_canvas.set_figure(result["fft_fig"])
        self.noise_canvas.set_figure(result["noise_fig"])

        snr = result["snr_db"]
        noise_power = -174 + 10 * np.log10(10e6) + 5 - snr
        self.lbl_noise.setText(f"{noise_power:.1f} dBm")

    def apply_params(self, params: dict):
        self.w_channel.setCurrentText(params.get("channel_model", "Rayleigh"))
        self.w_mod.setCurrentText(params.get("modulation", "QPSK"))
