"""
TX/RX Chain Visualization Tab
"""
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                  QGroupBox, QFormLayout, QComboBox, QSpinBox,
                                  QPushButton, QScrollArea, QFrame, QSplitter,
                                  QTextEdit, QSlider)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from gui.widgets import SectionHeader, MatplotlibCanvas
from core.modulation import generate_bits, modulate, demodulate, get_constellation
from core.channel_models import add_noise, apply_rayleigh, apply_rician
import utils.plotting as plt_utils


class SimWorker(QThread):
    """Worker thread for running modulation simulation."""
    result_ready = Signal(object)  # dict of results

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        p = self.params
        n_bits = p.get("n_bits", 5000)
        scheme = p.get("modulation", "BPSK")
        channel = p.get("channel", "AWGN")
        snr_db = p.get("snr_db", 10.0)

        bits = generate_bits(n_bits)
        tx_symbols = modulate(bits, scheme)
        # Apply channel
        if channel == "AWGN":
            rx_symbols = add_noise(tx_symbols, snr_db)
        elif channel == "Rayleigh":
            rx_symbols = apply_rayleigh(tx_symbols, snr_db)
        elif channel == "Rician":
            rx_symbols = apply_rician(tx_symbols, snr_db)
        else:
            rx_symbols = add_noise(tx_symbols, snr_db)

        rx_bits = demodulate(rx_symbols, scheme)
        n = min(len(bits), len(rx_bits))
        ber = np.mean(bits[:n] != rx_bits[:n])
        ideal = get_constellation(scheme)

        # Figures
        tx_fig = plt_utils.plot_waveform(tx_symbols, "TX Signal (Real)", 150)
        rx_fig = plt_utils.plot_waveform(rx_symbols, "RX Signal (Real)", 150)
        const_fig = plt_utils.plot_constellation(rx_symbols[:500], scheme, ideal)
        fft_fig = plt_utils.plot_fft_spectrum(tx_symbols, title="TX Spectrum")

        self.result_ready.emit({
            "bits_tx": bits[:64],
            "bits_rx": rx_bits[:64],
            "ber": ber,
            "tx_fig": tx_fig,
            "rx_fig": rx_fig,
            "const_fig": const_fig,
            "fft_fig": fft_fig,
            "n_bits": n_bits,
            "scheme": scheme,
            "channel": channel,
            "snr_db": snr_db,
        })


class TxRxTab(QWidget):
    """Transmitter/Receiver chain tab."""

    def __init__(self, simulation_state: dict, parent=None):
        super().__init__(parent)
        self.state = simulation_state
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Controls row
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("background: #12182E; border: 1px solid #1A2A4A; border-radius: 8px; padding: 12px;")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setSpacing(16)

        ctrl_layout.addWidget(QLabel("Modulation:"))
        self.w_mod = QComboBox()
        self.w_mod.addItems(["BPSK", "QPSK", "8PSK", "16QAM"])
        self.w_mod.setCurrentText("16QAM")
        ctrl_layout.addWidget(self.w_mod)

        ctrl_layout.addWidget(QLabel("Channel:"))
        self.w_ch = QComboBox()
        self.w_ch.addItems(["AWGN", "Rayleigh", "Rician"])
        self.w_ch.setCurrentText("Rayleigh")
        ctrl_layout.addWidget(self.w_ch)

        ctrl_layout.addWidget(QLabel("SNR:"))
        self.w_snr_lbl = QLabel("10 dB")
        self.w_snr_lbl.setStyleSheet("color: #00D4FF; font-weight: 700; background: transparent; min-width: 45px;")
        self.w_snr = QSlider(Qt.Horizontal)
        self.w_snr.setRange(-5, 30)
        self.w_snr.setValue(10)
        self.w_snr.setFixedWidth(140)
        self.w_snr.valueChanged.connect(lambda v: self.w_snr_lbl.setText(f"{v} dB"))
        ctrl_layout.addWidget(self.w_snr)
        ctrl_layout.addWidget(self.w_snr_lbl)

        ctrl_layout.addWidget(QLabel("Bits:"))
        self.w_nbits = QComboBox()
        self.w_nbits.addItems(["1000", "5000", "10000", "50000"])
        self.w_nbits.setCurrentText("5000")
        ctrl_layout.addWidget(self.w_nbits)

        ctrl_layout.addStretch()
        self.btn_run = QPushButton("▶  Run Simulation")
        self.btn_run.setObjectName("primary")
        self.btn_run.setMinimumHeight(34)
        self.btn_run.clicked.connect(self._run)
        ctrl_layout.addWidget(self.btn_run)

        layout.addWidget(ctrl_frame)

        # BER display
        self.ber_label = QLabel("BER: —")
        self.ber_label.setStyleSheet(
            "color: #00D4FF; font-size: 16px; font-weight: 700; "
            "background: #12182E; border: 1px solid #1A2A4A; "
            "border-radius: 6px; padding: 8px 16px;"
        )
        layout.addWidget(self.ber_label)

        # Bit stream display
        bit_frame = QFrame()
        bit_frame.setStyleSheet("background: #0F1629; border: 1px solid #1A2A4A; border-radius: 8px;")
        bit_layout = QHBoxLayout(bit_frame)
        bit_layout.setSpacing(10)

        tx_grp = QGroupBox("TX Bit Stream (first 64 bits)")
        tx_vl = QVBoxLayout(tx_grp)
        self.tx_bits_lbl = QLabel("—")
        self.tx_bits_lbl.setWordWrap(True)
        self.tx_bits_lbl.setStyleSheet(
            "color: #00FF88; font-family: 'Courier New', monospace; "
            "font-size: 11px; background: transparent; letter-spacing: 2px;"
        )
        tx_vl.addWidget(self.tx_bits_lbl)
        bit_layout.addWidget(tx_grp)

        rx_grp = QGroupBox("RX Bit Stream (decoded)")
        rx_vl = QVBoxLayout(rx_grp)
        self.rx_bits_lbl = QLabel("—")
        self.rx_bits_lbl.setWordWrap(True)
        self.rx_bits_lbl.setStyleSheet(
            "color: #FF6B6B; font-family: 'Courier New', monospace; "
            "font-size: 11px; background: transparent; letter-spacing: 2px;"
        )
        rx_vl.addWidget(self.rx_bits_lbl)
        bit_layout.addWidget(rx_grp)

        layout.addWidget(bit_frame)

        # Plot area
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(4)

        # Left: waveforms
        left_widget = QWidget()
        left_vl = QVBoxLayout(left_widget)
        left_vl.setContentsMargins(0, 0, 0, 0)
        left_vl.setSpacing(8)
        self.tx_canvas = MatplotlibCanvas()
        self.rx_canvas = MatplotlibCanvas()
        self.fft_canvas = MatplotlibCanvas()
        left_vl.addWidget(QLabel("TX Waveform"))
        left_vl.addWidget(self.tx_canvas)
        left_vl.addWidget(QLabel("RX Waveform (after channel)"))
        left_vl.addWidget(self.rx_canvas)
        left_vl.addWidget(QLabel("FFT Spectrum"))
        left_vl.addWidget(self.fft_canvas)

        # Right: constellation
        right_widget = QWidget()
        right_vl = QVBoxLayout(right_widget)
        right_vl.setContentsMargins(0, 0, 0, 0)
        self.const_canvas = MatplotlibCanvas()
        right_vl.addWidget(QLabel("Constellation Diagram"))
        right_vl.addWidget(self.const_canvas)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400])

        layout.addWidget(splitter, 1)

    def _run(self):
        if self._worker and self._worker.isRunning():
            return
        self.btn_run.setEnabled(False)
        self.btn_run.setText("⏳ Running...")
        params = {
            "modulation": self.w_mod.currentText(),
            "channel": self.w_ch.currentText(),
            "snr_db": float(self.w_snr.value()),
            "n_bits": int(self.w_nbits.currentText()),
        }
        self._worker = SimWorker(params)
        self._worker.result_ready.connect(self._on_result)
        self._worker.start()

    def _on_result(self, result: dict):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("▶  Run Simulation")

        ber = result["ber"]
        self.ber_label.setText(
            f"BER: {ber:.4e}  |  {result['scheme']} over {result['channel']}  "
            f"|  SNR = {result['snr_db']} dB  |  Bits: {result['n_bits']:,}"
        )

        # Bit streams
        tx_str = " ".join(str(b) for b in result["bits_tx"])
        rx_str = " ".join(str(b) for b in result["bits_rx"][:64])
        self.tx_bits_lbl.setText(tx_str)
        self.rx_bits_lbl.setText(rx_str)

        self.tx_canvas.set_figure(result["tx_fig"])
        self.rx_canvas.set_figure(result["rx_fig"])
        self.const_canvas.set_figure(result["const_fig"])
        self.fft_canvas.set_figure(result["fft_fig"])

        # Update state
        self.state.setdefault("kpis", {})["avg_ber"] = ber

    def apply_params(self, params: dict):
        self.w_mod.setCurrentText(params.get("modulation", "16QAM"))
        self.w_ch.setCurrentText(params.get("channel_model", "Rayleigh"))
