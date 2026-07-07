"""
Parameter Configuration Tab
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                  QGroupBox, QFormLayout, QDoubleSpinBox,
                                  QSpinBox, QComboBox, QSlider, QPushButton,
                                  QScrollArea, QFrame, QGridLayout, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from gui.widgets import SectionHeader


class ParameterTab(QWidget):
    """Parameter configuration with validation."""

    params_applied = Signal(dict)

    DEFAULTS = {
        "path_loss_exp": 3.5,
        "tx_power_dbm": 43.0,
        "carrier_freq_ghz": 2.1,
        "channel_model": "Rayleigh",
        "bandwidth_mhz": 10.0,
        "noise_figure_db": 5.0,
        "n_base_stations": 4,
        "n_ues": 12,
        "area_size_m": 1000.0,
        "modulation": "16QAM",
        "snr_min": -5,
        "snr_max": 30,
        "handover_hyst_db": 3.0,
        "scheduler": "Proportional Fair",
        "numerology": "15 kHz",
        "n_resource_blocks": 25,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_params = dict(self.DEFAULTS)
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)
        scroll.setWidget(container)

        layout.addWidget(SectionHeader("Radio Parameters"))

        # Radio group
        radio_group = QGroupBox("RF Configuration")
        radio_form = QFormLayout(radio_group)
        radio_form.setSpacing(10)
        radio_form.setLabelAlignment(Qt.AlignRight)

        self.w_tx_power = QDoubleSpinBox()
        self.w_tx_power.setRange(20, 60)
        self.w_tx_power.setValue(43)
        self.w_tx_power.setSuffix(" dBm")
        self.w_tx_power.setToolTip("Base station transmit power (dBm)")
        radio_form.addRow("Tx Power:", self.w_tx_power)

        self.w_carrier_freq = QDoubleSpinBox()
        self.w_carrier_freq.setRange(0.7, 40.0)
        self.w_carrier_freq.setValue(2.1)
        self.w_carrier_freq.setSuffix(" GHz")
        self.w_carrier_freq.setDecimals(3)
        self.w_carrier_freq.setToolTip("Carrier frequency (GHz)")
        radio_form.addRow("Carrier Freq:", self.w_carrier_freq)

        self.w_bandwidth = QDoubleSpinBox()
        self.w_bandwidth.setRange(1.4, 100)
        self.w_bandwidth.setValue(10)
        self.w_bandwidth.setSuffix(" MHz")
        self.w_bandwidth.setToolTip("Channel bandwidth (MHz)")
        radio_form.addRow("Bandwidth:", self.w_bandwidth)

        self.w_path_loss = QDoubleSpinBox()
        self.w_path_loss.setRange(2.0, 6.0)
        self.w_path_loss.setValue(3.5)
        self.w_path_loss.setDecimals(1)
        self.w_path_loss.setSingleStep(0.1)
        self.w_path_loss.setToolTip("Path loss exponent (2=free space, 3.5=urban)")
        radio_form.addRow("Path Loss Exp:", self.w_path_loss)

        self.w_noise_fig = QDoubleSpinBox()
        self.w_noise_fig.setRange(0, 20)
        self.w_noise_fig.setValue(5)
        self.w_noise_fig.setSuffix(" dB")
        self.w_noise_fig.setToolTip("Receiver noise figure (dB)")
        radio_form.addRow("Noise Figure:", self.w_noise_fig)

        layout.addWidget(radio_group)

        # Channel group
        ch_group = QGroupBox("Channel Model")
        ch_form = QFormLayout(ch_group)
        ch_form.setSpacing(10)
        ch_form.setLabelAlignment(Qt.AlignRight)

        self.w_channel = QComboBox()
        self.w_channel.addItems(["AWGN", "Rayleigh", "Rician"])
        self.w_channel.setCurrentText("Rayleigh")
        self.w_channel.setToolTip("Wireless channel propagation model")
        ch_form.addRow("Channel Model:", self.w_channel)

        self.w_modulation = QComboBox()
        self.w_modulation.addItems(["BPSK", "QPSK", "8PSK", "16QAM"])
        self.w_modulation.setCurrentText("16QAM")
        self.w_modulation.setToolTip("Digital modulation scheme")
        ch_form.addRow("Modulation:", self.w_modulation)

        snr_row = QHBoxLayout()
        self.w_snr_min = QSpinBox()
        self.w_snr_min.setRange(-20, 10)
        self.w_snr_min.setValue(-5)
        self.w_snr_min.setSuffix(" dB")
        self.w_snr_max = QSpinBox()
        self.w_snr_max.setRange(10, 50)
        self.w_snr_max.setValue(30)
        self.w_snr_max.setSuffix(" dB")
        snr_row.addWidget(self.w_snr_min)
        snr_row.addWidget(QLabel("to"))
        snr_row.addWidget(self.w_snr_max)
        ch_form.addRow("SNR Range:", snr_row)

        layout.addWidget(ch_group)

        # Network group
        net_group = QGroupBox("Network Configuration")
        net_form = QFormLayout(net_group)
        net_form.setSpacing(10)
        net_form.setLabelAlignment(Qt.AlignRight)

        self.w_n_bs = QSpinBox()
        self.w_n_bs.setRange(1, 12)
        self.w_n_bs.setValue(4)
        self.w_n_bs.setToolTip("Number of base stations")
        net_form.addRow("Base Stations:", self.w_n_bs)

        self.w_n_ues = QSpinBox()
        self.w_n_ues.setRange(1, 50)
        self.w_n_ues.setValue(12)
        self.w_n_ues.setToolTip("Number of user equipment devices")
        net_form.addRow("UE Count:", self.w_n_ues)

        self.w_area = QDoubleSpinBox()
        self.w_area.setRange(100, 5000)
        self.w_area.setValue(1000)
        self.w_area.setSuffix(" m")
        self.w_area.setToolTip("Simulation area size (meters)")
        net_form.addRow("Area Size:", self.w_area)

        self.w_ho_hyst = QDoubleSpinBox()
        self.w_ho_hyst.setRange(0, 10)
        self.w_ho_hyst.setValue(3)
        self.w_ho_hyst.setSuffix(" dB")
        self.w_ho_hyst.setToolTip("A3 handover hysteresis margin")
        net_form.addRow("HO Hysteresis:", self.w_ho_hyst)

        self.w_scheduler = QComboBox()
        self.w_scheduler.addItems(["Proportional Fair", "Round Robin", "Max SINR"])
        self.w_scheduler.setToolTip("Resource allocation scheduler type")
        net_form.addRow("Scheduler:", self.w_scheduler)

        layout.addWidget(net_group)

        # 5G / Numerology group
        nr_group = QGroupBox("5G NR Parameters")
        nr_form = QFormLayout(nr_group)
        nr_form.setSpacing(10)
        nr_form.setLabelAlignment(Qt.AlignRight)

        self.w_numerology = QComboBox()
        self.w_numerology.addItems(["15 kHz (μ=0)", "30 kHz (μ=1)", "60 kHz (μ=2)"])
        self.w_numerology.setToolTip("5G NR subcarrier spacing numerology")
        nr_form.addRow("Numerology:", self.w_numerology)

        self.w_n_rb = QSpinBox()
        self.w_n_rb.setRange(6, 132)
        self.w_n_rb.setValue(25)
        self.w_n_rb.setToolTip("Number of resource blocks (10 MHz ≈ 50 RBs)")
        nr_form.addRow("Resource Blocks:", self.w_n_rb)

        layout.addWidget(nr_group)

        # Buttons
        btn_row = QHBoxLayout()
        btn_apply = QPushButton("▶  Apply Parameters")
        btn_apply.setObjectName("primary")
        btn_apply.setMinimumHeight(38)
        btn_apply.clicked.connect(self._apply)
        btn_apply.setToolTip("Apply the configured parameters to the simulation")

        btn_reset = QPushButton("↺  Reset to Defaults")
        btn_reset.setMinimumHeight(38)
        btn_reset.clicked.connect(self._reset)
        btn_reset.setToolTip("Reset all parameters to factory defaults")

        btn_row.addWidget(btn_apply)
        btn_row.addWidget(btn_reset)
        layout.addLayout(btn_row)

        # Validation label
        self._validation_label = QLabel("")
        self._validation_label.setStyleSheet("color: #00FF88; font-size: 10px; background: transparent;")
        layout.addWidget(self._validation_label)

        layout.addStretch()

    def _apply(self):
        params = {
            "path_loss_exp": self.w_path_loss.value(),
            "tx_power_dbm": self.w_tx_power.value(),
            "carrier_freq_ghz": self.w_carrier_freq.value(),
            "channel_model": self.w_channel.currentText(),
            "bandwidth_mhz": self.w_bandwidth.value(),
            "noise_figure_db": self.w_noise_fig.value(),
            "n_base_stations": self.w_n_bs.value(),
            "n_ues": self.w_n_ues.value(),
            "area_size_m": self.w_area.value(),
            "modulation": self.w_modulation.currentText(),
            "snr_min": self.w_snr_min.value(),
            "snr_max": self.w_snr_max.value(),
            "handover_hyst_db": self.w_ho_hyst.value(),
            "scheduler": self.w_scheduler.currentText(),
            "numerology": self.w_numerology.currentText(),
            "n_resource_blocks": self.w_n_rb.value(),
        }
        self.current_params = params
        self.params_applied.emit(params)
        self._validation_label.setText("✓ Parameters applied successfully")
        self._validation_label.setStyleSheet("color: #00FF88; font-size: 10px; background: transparent;")

    def _reset(self):
        p = self.DEFAULTS
        self.w_path_loss.setValue(p["path_loss_exp"])
        self.w_tx_power.setValue(p["tx_power_dbm"])
        self.w_carrier_freq.setValue(p["carrier_freq_ghz"])
        self.w_channel.setCurrentText(p["channel_model"])
        self.w_bandwidth.setValue(p["bandwidth_mhz"])
        self.w_noise_fig.setValue(p["noise_figure_db"])
        self.w_n_bs.setValue(p["n_base_stations"])
        self.w_n_ues.setValue(p["n_ues"])
        self.w_area.setValue(p["area_size_m"])
        self.w_modulation.setCurrentText(p["modulation"])
        self.w_snr_min.setValue(p["snr_min"])
        self.w_snr_max.setValue(p["snr_max"])
        self.w_ho_hyst.setValue(p["handover_hyst_db"])
        self.w_scheduler.setCurrentText(p["scheduler"])
        self.w_numerology.setCurrentText(p["numerology"])
        self.w_n_rb.setValue(p["n_resource_blocks"])
        self._validation_label.setText("↺ Parameters reset to defaults")
        self._validation_label.setStyleSheet("color: #FFB800; font-size: 10px; background: transparent;")

    def get_params(self) -> dict:
        return self.current_params
