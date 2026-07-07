"""
Main Application Window
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                                  QStatusBar, QLabel, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QColor

from gui.styles import MAIN_STYLESHEET
from gui.dashboard_tab import DashboardTab
from gui.parameter_tab import ParameterTab
from gui.tx_rx_tab import TxRxTab
from gui.channel_tab import ChannelTab
from gui.results_tab import ResultsTab
from gui.comparison_tab import ComparisonTab
from gui.analysis_tab import AnalysisTab
from gui.fiveg_tab import FiveGTab
from gui.ai_tab import AITab
from gui.report_tab import ReportTab
from gui.widgets import StatusLED
import datetime


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mobile Communication System Simulator")
        self.setMinimumSize(1200, 800)
        self.resize(1440, 900)

        # Shared simulation state
        self.simulation_state = {
            "running": False,
            "sim_time": 0.0,
            "kpis": {
                "avg_sinr": None,
                "handoff_count": 0,
                "active_users": 0,
                "cell_load": None,
                "avg_throughput": None,
                "avg_ber": None,
            }
        }
        self.params = {}

        self.setStyleSheet(MAIN_STYLESHEET)
        self._setup_ui()
        self._setup_statusbar()

        # Clock update
        self._clock_timer = QTimer()
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top header bar
        header = self._build_header()
        main_layout.addWidget(header)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(False)
        self.tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.tabs, 1)

        # Create tabs
        self.dashboard_tab = DashboardTab(self.simulation_state)
        self.param_tab = ParameterTab()
        self.txrx_tab = TxRxTab(self.simulation_state)
        self.channel_tab = ChannelTab(self.simulation_state)
        self.results_tab = ResultsTab(self.simulation_state)
        self.comparison_tab = ComparisonTab(self.simulation_state)
        self.analysis_tab = AnalysisTab(self.simulation_state, self.params)
        self.fiveg_tab = FiveGTab(self.simulation_state)
        self.ai_tab = AITab(self.simulation_state)
        self.report_tab = ReportTab(self.simulation_state, self.params)

        self.tabs.addTab(self.dashboard_tab,    "🏠  Dashboard")
        self.tabs.addTab(self.param_tab,         "⚙️  Parameters")
        self.tabs.addTab(self.txrx_tab,          "📡  TX / RX")
        self.tabs.addTab(self.channel_tab,       "🌊  Channel")
        self.tabs.addTab(self.results_tab,       "📈  Results")
        self.tabs.addTab(self.comparison_tab,    "🔍  Compare")
        self.tabs.addTab(self.analysis_tab,      "🗺️  Network")
        self.tabs.addTab(self.fiveg_tab,         "5️⃣G  5G NR")
        self.tabs.addTab(self.ai_tab,            "🤖  AI Model")
        self.tabs.addTab(self.report_tab,        "📄  Report")

        # Connect parameter changes
        self.param_tab.params_applied.connect(self._on_params_applied)

        # Set initial params
        self._on_params_applied(self.param_tab.get_params())

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setFixedHeight(46)
        header.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #060810, stop:0.4 #0A0E1A, stop:1 #060810);"
            "border-bottom: 1px solid #1A2A4A;"
        )
        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(12)

        # Logo text
        logo = QLabel("◈ COMM-SIM")
        logo.setStyleSheet(
            "color: #00D4FF; font-size: 14px; font-weight: 700; "
            "letter-spacing: 3px; background: transparent;"
        )
        layout.addWidget(logo)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color: #1A2A4A; max-height: 24px;")
        layout.addWidget(sep)

        subtitle = QLabel("Mobile Communication System Simulator")
        subtitle.setStyleSheet(
            "color: #4A5680; font-size: 11px; background: transparent; letter-spacing: 0.5px;"
        )
        layout.addWidget(subtitle)
        layout.addStretch()

        # Status LED
        self._header_led = StatusLED("#00D4FF")
        layout.addWidget(self._header_led)
        self._header_status = QLabel("IDLE")
        self._header_status.setStyleSheet(
            "color: #4A5680; font-size: 9px; letter-spacing: 2px; background: transparent;"
        )
        layout.addWidget(self._header_status)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("color: #1A2A4A; max-height: 24px;")
        layout.addWidget(sep2)

        self._clock_lbl = QLabel("")
        self._clock_lbl.setStyleSheet(
            "color: #4A5680; font-size: 10px; font-family: 'Courier New'; background: transparent;"
        )
        layout.addWidget(self._clock_lbl)

        return header

    def _setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._sb_main = QLabel("Ready")
        self._sb_main.setStyleSheet("color: #8090B0;")
        self.status_bar.addWidget(self._sb_main)
        self.status_bar.addPermanentWidget(QLabel("Python / PySide6  |  "))
        self._sb_version = QLabel("v2.0")
        self._sb_version.setStyleSheet("color: #00D4FF;")
        self.status_bar.addPermanentWidget(self._sb_version)

    def _update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self._clock_lbl.setText(now)

        # Update sim time
        if self.simulation_state.get("running"):
            self.simulation_state["sim_time"] = self.simulation_state.get("sim_time", 0.0) + 1.0
            self._sb_main.setText(f"Simulation running — {self.simulation_state['sim_time']:.0f}s")
            self._header_status.setText("RUNNING")
            self._header_status.setStyleSheet(
                "color: #00D4FF; font-size: 9px; letter-spacing: 2px; background: transparent;"
            )
        else:
            self._header_status.setText("IDLE")
            self._header_status.setStyleSheet(
                "color: #4A5680; font-size: 9px; letter-spacing: 2px; background: transparent;"
            )

    def _on_params_applied(self, params: dict):
        self.params.update(params)
        self.analysis_tab.update_params(params)
        self.report_tab.update_params(params)
        self.txrx_tab.apply_params(params)
        self.channel_tab.apply_params(params)
        self._sb_main.setText(
            f"Parameters applied — {params.get('modulation', '?')} | "
            f"{params.get('channel_model', '?')} | "
            f"{params.get('n_base_stations', '?')} BSs | "
            f"{params.get('n_ues', '?')} UEs"
        )

    def closeEvent(self, event):
        # Stop any running workers
        super().closeEvent(event)
