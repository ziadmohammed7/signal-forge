"""
Report Generation Tab: Collect results and export PDF.
"""
import os
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                  QPushButton, QFrame, QFileDialog, QTextEdit,
                                  QGroupBox, QFormLayout, QLineEdit, QScrollArea,
                                  QProgressBar, QCheckBox, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
from gui.widgets import SectionHeader
from utils.pdf_report import generate_pdf_report
import utils.plotting as plt_utils
from core.modulation import compute_ber, generate_bits, modulate, get_constellation
from core.channel_models import add_noise


class ReportWorker(QThread):
    progress = Signal(str)
    finished = Signal(bytes, str)
    error = Signal(str)

    def __init__(self, params, kpis, output_path):
        super().__init__()
        self.params = params
        self.kpis = kpis
        self.output_path = output_path

    def run(self):
        try:
            self.progress.emit("Generating plots...")
            figures = []

            # BER plot
            schemes = ["BPSK", "QPSK", "16QAM"]
            snr_range = np.arange(-5, 31, 1)
            ber_dict = {}
            for s in schemes:
                self.progress.emit(f"Computing BER for {s}...")
                ber_dict[s] = compute_ber(snr_range, s, "AWGN", n_bits=10000)
            ber_fig = plt_utils.plot_ber_vs_snr(snr_range, ber_dict, "BER vs SNR (AWGN)")
            figures.append(("BER vs SNR Comparison", ber_fig))

            # Constellation
            self.progress.emit("Generating constellation plots...")
            bits = generate_bits(3000)
            syms = modulate(bits, "16QAM")
            rx = add_noise(syms, 15)
            ideal = get_constellation("16QAM")
            const_fig = plt_utils.plot_constellation(rx[:400], "16QAM", ideal)
            figures.append(("16QAM Constellation (SNR=15dB)", const_fig))

            # Spectrum
            tx_fig = plt_utils.plot_fft_spectrum(syms, title="16QAM TX Spectrum")
            figures.append(("TX FFT Spectrum", tx_fig))

            self.progress.emit("Building PDF...")
            pdf_bytes = generate_pdf_report(self.params, self.kpis, figures, self.output_path)
            self.finished.emit(pdf_bytes, self.output_path)
        except Exception as e:
            self.error.emit(str(e))


class ReportTab(QWidget):
    """PDF report generation tab."""

    def __init__(self, simulation_state: dict, params_ref: dict, parent=None):
        super().__init__(parent)
        self.state = simulation_state
        self.params = params_ref
        self._worker = None
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
        layout.setSpacing(16)
        scroll.setWidget(container)

        layout.addWidget(SectionHeader("Report Configuration"))

        # Header info
        header_grp = QGroupBox("Report Header")
        header_form = QFormLayout(header_grp)
        header_form.setSpacing(10)

        self.w_title = QLineEdit("Mobile Communication System Simulation Report")
        self.w_author = QLineEdit("Graduation Project")
        self.w_institution = QLineEdit("Faculty of Engineering")
        header_form.addRow("Report Title:", self.w_title)
        header_form.addRow("Author:", self.w_author)
        header_form.addRow("Institution:", self.w_institution)
        layout.addWidget(header_grp)

        # Sections to include
        sections_grp = QGroupBox("Sections to Include")
        sections_vl = QVBoxLayout(sections_grp)
        self._section_checks = {}
        for section in ["BER vs SNR Curves", "Constellation Diagrams", "FFT Spectrum",
                          "KPI Summary", "Simulation Parameters", "Network Topology"]:
            cb = QCheckBox(section)
            cb.setChecked(True)
            sections_vl.addWidget(cb)
            self._section_checks[section] = cb
        layout.addWidget(sections_grp)

        # Output path
        path_grp = QGroupBox("Output File")
        path_layout = QHBoxLayout(path_grp)
        self.w_path = QLineEdit(os.path.expanduser("~/simulation_report.pdf"))
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse)
        path_layout.addWidget(self.w_path)
        path_layout.addWidget(btn_browse)
        layout.addWidget(path_grp)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_lbl = QLabel("Configure report and click Generate.")
        self.status_lbl.setStyleSheet("color: #8090B0; font-size: 10px; background: transparent;")
        layout.addWidget(self.status_lbl)

        # Generate button
        btn_generate = QPushButton("📄  Generate PDF Report")
        btn_generate.setObjectName("success")
        btn_generate.setMinimumHeight(44)
        btn_generate.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #006644, stop:1 #00FF88); color: #000814; "
            "font-weight: 700; font-size: 13px; border-radius: 6px;"
        )
        btn_generate.clicked.connect(self._generate)
        layout.addWidget(btn_generate)

        # Log area
        log_grp = QGroupBox("Generation Log")
        log_vl = QVBoxLayout(log_grp)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(160)
        self.log_area.setStyleSheet(
            "background: #060810; color: #8090B0; font-family: 'Courier New'; "
            "font-size: 10px; border: 1px solid #1A2A4A; border-radius: 4px;"
        )
        log_vl.addWidget(self.log_area)
        layout.addWidget(log_grp)

        layout.addStretch()

    def _browse(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Report", self.w_path.text(),
                                               "PDF (*.pdf)")
        if path:
            self.w_path.setText(path)

    def _log(self, msg):
        self.log_area.append(f"[LOG] {msg}")
        self.status_lbl.setText(msg)
        self.status_lbl.setStyleSheet("color: #00D4FF; font-size: 10px; background: transparent;")

    def _generate(self):
        if self._worker and self._worker.isRunning():
            return
        path = self.w_path.text().strip()
        if not path.endswith(".pdf"):
            path += ".pdf"
        self.w_path.setText(path)
        self.progress_bar.setVisible(True)
        self.log_area.clear()
        self._log("Starting report generation...")

        kpis = self.state.get("kpis", {})
        params_for_report = {
            "Tx Power": f"{self.params.get('tx_power_dbm', 43)} dBm",
            "Carrier Freq": f"{self.params.get('carrier_freq_ghz', 2.1)} GHz",
            "Bandwidth": f"{self.params.get('bandwidth_mhz', 10)} MHz",
            "Channel Model": self.params.get("channel_model", "Rayleigh"),
            "Path Loss Exp": self.params.get("path_loss_exp", 3.5),
            "Noise Figure": f"{self.params.get('noise_figure_db', 5)} dB",
            "Base Stations": self.params.get("n_base_stations", 4),
            "UE Count": self.params.get("n_ues", 12),
            "Area Size": f"{self.params.get('area_size_m', 1000)} m",
            "Modulation": self.params.get("modulation", "16QAM"),
            "Scheduler": self.params.get("scheduler", "Proportional Fair"),
            "HO Hysteresis": f"{self.params.get('handover_hyst_db', 3)} dB",
            "Numerology": self.params.get("numerology", "15 kHz"),
            "Resource Blocks": self.params.get("n_resource_blocks", 25),
        }

        self._worker = ReportWorker(params_for_report, kpis, path)
        self._worker.progress.connect(self._log)
        self._worker.finished.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_done(self, pdf_bytes, path):
        self.progress_bar.setVisible(False)
        self._log(f"✓ Report saved: {path}")
        self.status_lbl.setStyleSheet("color: #00FF88; font-size: 10px; background: transparent;")
        QMessageBox.information(self, "Report Generated",
                                 f"PDF report successfully saved to:\n{path}")

    def _on_error(self, msg):
        self.progress_bar.setVisible(False)
        self._log(f"ERROR: {msg}")
        self.status_lbl.setStyleSheet("color: #FF4560; font-size: 10px; background: transparent;")
        QMessageBox.critical(self, "Error", f"Failed to generate report:\n{msg}")

    def update_params(self, params: dict):
        self.params.update(params)
