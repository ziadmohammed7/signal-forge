"""
Mobile Communication Analysis Tab
Multi-cell network with SINR heatmap, handover, mobility, topology.
"""
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                  QPushButton, QFrame, QTabWidget, QSpinBox,
                                  QDoubleSpinBox, QGroupBox, QFormLayout,
                                  QProgressBar, QSplitter)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from gui.widgets import SectionHeader, MatplotlibCanvas
from core.sinr import BaseStation, compute_sinr_heatmap, compute_network_sinr, find_best_cell
from core.mobility import UE, RandomWaypointMobility
from core.handover import A3HandoverManager, HandoverStats
from core.scheduler import ProportionalFairScheduler
from core.ai_model import HandoverPredictor
import utils.plotting as plt_utils


class NetworkSimWorker(QThread):
    status = Signal(str)
    heatmap_ready = Signal(object)  # (heatmap, bss, ues)
    topology_ready = Signal(object)
    kpis_ready = Signal(dict)

    def __init__(self, params):
        super().__init__()
        self.params = params
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        p = self.params
        area = p.get("area_size_m", 1000.0)
        n_bs = p.get("n_base_stations", 4)
        n_ues = p.get("n_ues", 12)
        tx_pwr = p.get("tx_power_dbm", 43.0)
        freq = p.get("carrier_freq_ghz", 2.1) * 1e9
        bw = p.get("bandwidth_mhz", 10.0) * 1e6
        nf = p.get("noise_figure_db", 5.0)
        pl_exp = p.get("path_loss_exp", 3.5)
        ho_hyst = p.get("handover_hyst_db", 3.0)
        resolution = p.get("heatmap_resolution", 40)

        # Create base stations in a grid
        bss = []
        positions = _grid_positions(n_bs, area)
        for i, (bx, by) in enumerate(positions):
            bs = BaseStation(i, bx, by, tx_pwr, freq, bw, nf, pl_exp)
            bss.append(bs)

        # Create UEs
        mob = RandomWaypointMobility(area)
        ues = []
        for j in range(n_ues):
            ue = UE(j, np.random.uniform(0, area), np.random.uniform(0, area))
            mob.add_ue(ue)
            ues.append(ue)

        ho_mgr = A3HandoverManager(hysteresis_db=ho_hyst)
        ho_stats = HandoverStats()
        scheduler = ProportionalFairScheduler(n_resource_blocks=p.get("n_resource_blocks", 25))
        predictor = HandoverPredictor()

        # Initial assignment
        for ue in ues:
            ue.serving_cell = find_best_cell(bss, ue.x, ue.y)

        self.status.emit("Computing SINR heatmap...")
        heatmap = compute_sinr_heatmap(bss, area, resolution, bw, nf)
        self.heatmap_ready.emit((heatmap, bss, list(ues)))

        # Run mobility + handover for N steps
        n_steps = 20
        for step in range(n_steps):
            if self._stop:
                break
            self.status.emit(f"Simulating step {step+1}/{n_steps}...")
            mob.step(dt=2.0)

            # Update SINR and handover
            for ue in ues:
                if ue.serving_cell is None:
                    ue.serving_cell = find_best_cell(bss, ue.x, ue.y)
                    continue
                ue.sinr = compute_network_sinr(bss, ue.x, ue.y, ue.serving_cell, nf, bw)
                # AI prediction
                best_id = find_best_cell(bss, ue.x, ue.y)
                best_bs = next((b for b in bss if b.id == best_id), None)
                srv_bs = next((b for b in bss if b.id == ue.serving_cell), None)
                if best_bs and srv_bs:
                    dist_serving = np.hypot(ue.x - srv_bs.x, ue.y - srv_bs.y)
                    dist_best = np.hypot(ue.x - best_bs.x, ue.y - best_bs.y)
                    best_sinr = compute_network_sinr(bss, ue.x, ue.y, best_id, nf, bw)
                    predictor.record_sample(ue.sinr, best_sinr, dist_serving, dist_best,
                                             best_id != ue.serving_cell)

                def _sinr_fn(bs_id, ux, uy):
                    return compute_network_sinr(bss, ux, uy, bs_id, nf, bw)

                new_cell = ho_mgr.evaluate(ue, bss, _sinr_fn, dt=2.0)
                if new_cell is not None:
                    ho_stats.record(step * 2.0, ue.id, ue.serving_cell, new_cell)
                    ue.serving_cell = new_cell
                    ue.handover_count += 1

            # Schedule
            for bs in bss:
                bs_ues = [u for u in ues if u.serving_cell == bs.id]
                if bs_ues:
                    scheduler.schedule(bs_ues, None)

        # Compute final KPIs
        sinrs = [ue.sinr for ue in ues if ue.sinr > -100]
        avg_sinr = np.mean(sinrs) if sinrs else 0.0
        tps = [ue.throughput for ue in ues]
        avg_tp = np.mean(tps) if tps else 0.0
        loads = []
        for bs in bss:
            n_c = sum(1 for u in ues if u.serving_cell == bs.id)
            loads.append(n_c / max(n_ues, 1))
        avg_load = np.mean(loads) if loads else 0.0

        kpis = {
            "avg_sinr": avg_sinr,
            "handoff_count": ho_stats.total_handovers,
            "active_users": n_ues,
            "cell_load": avg_load,
            "avg_throughput": avg_tp,
        }
        self.kpis_ready.emit(kpis)
        self.topology_ready.emit((bss, list(ues), area))
        self.status.emit(f"Simulation complete. Total handovers: {ho_stats.total_handovers}")


def _grid_positions(n, area):
    """Generate grid positions for base stations."""
    cols = int(np.ceil(np.sqrt(n)))
    rows = int(np.ceil(n / cols))
    positions = []
    for r in range(rows):
        for c in range(cols):
            if len(positions) >= n:
                break
            x = (c + 1) * area / (cols + 1)
            y = (r + 1) * area / (rows + 1)
            positions.append((x, y))
    return positions[:n]


class AnalysisTab(QWidget):
    """Multi-cell network analysis tab."""

    def __init__(self, simulation_state: dict, params_ref: dict, parent=None):
        super().__init__(parent)
        self.state = simulation_state
        self.params = params_ref
        self._worker = None
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

        ctrl.addWidget(QLabel("Resolution:"))
        self.w_res = QSpinBox()
        self.w_res.setRange(20, 80)
        self.w_res.setValue(40)
        self.w_res.setToolTip("Heatmap grid resolution (higher = slower)")
        ctrl.addWidget(self.w_res)

        ctrl.addStretch()

        self.btn_run = QPushButton("▶  Run Network Simulation")
        self.btn_run.setObjectName("primary")
        self.btn_run.setMinimumHeight(36)
        self.btn_run.clicked.connect(self._run)
        ctrl.addWidget(self.btn_run)

        self.btn_stop = QPushButton("⏹  Stop")
        self.btn_stop.setObjectName("danger")
        self.btn_stop.setMinimumHeight(36)
        self.btn_stop.clicked.connect(self._stop)
        self.btn_stop.setEnabled(False)
        ctrl.addWidget(self.btn_stop)

        layout.addWidget(ctrl_frame)

        self.status_lbl = QLabel("Ready. Configure parameters and run simulation.")
        self.status_lbl.setStyleSheet("color: #8090B0; font-size: 10px; background: transparent;")
        layout.addWidget(self.status_lbl)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Plots
        sub_tabs = QTabWidget()
        sub_tabs.setStyleSheet("QTabBar::tab { min-width: 90px; padding: 6px 12px; font-size: 10px; }")
        layout.addWidget(sub_tabs, 1)

        # Heatmap tab
        hm_widget = QWidget()
        hm_vl = QVBoxLayout(hm_widget)
        hm_vl.setContentsMargins(4, 4, 4, 4)
        self.heatmap_canvas = MatplotlibCanvas()
        hm_vl.addWidget(self.heatmap_canvas)
        sub_tabs.addTab(hm_widget, "🗺️ SINR Heatmap")

        # Topology tab
        topo_widget = QWidget()
        topo_vl = QVBoxLayout(topo_widget)
        topo_vl.setContentsMargins(4, 4, 4, 4)
        self.topo_canvas = MatplotlibCanvas()
        topo_vl.addWidget(self.topo_canvas)
        sub_tabs.addTab(topo_widget, "🌐 Network Topology")

        # KPI display
        kpi_widget = QWidget()
        kpi_vl = QVBoxLayout(kpi_widget)
        kpi_vl.setContentsMargins(10, 10, 10, 10)
        self.kpi_display = QLabel("Run simulation to see KPIs.")
        self.kpi_display.setStyleSheet(
            "color: #C8D6F0; font-size: 13px; background: #0F1629; "
            "border: 1px solid #1A2A4A; border-radius: 8px; padding: 20px;"
        )
        self.kpi_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.kpi_display.setWordWrap(True)
        kpi_vl.addWidget(self.kpi_display)
        kpi_vl.addStretch()
        sub_tabs.addTab(kpi_widget, "📊 KPI Report")

    def _run(self):
        if self._worker and self._worker.isRunning():
            return
        params = dict(self.params)
        params["heatmap_resolution"] = self.w_res.value()

        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress.setVisible(True)
        self.state["running"] = True

        self._worker = NetworkSimWorker(params)
        self._worker.status.connect(self._on_status)
        self._worker.heatmap_ready.connect(self._on_heatmap)
        self._worker.topology_ready.connect(self._on_topology)
        self._worker.kpis_ready.connect(self._on_kpis)
        self._worker.finished.connect(self._on_done)
        self._worker.start()

    def _stop(self):
        if self._worker:
            self._worker.stop()

    def _on_status(self, msg):
        self.status_lbl.setText(msg)
        self.status_lbl.setStyleSheet("color: #00D4FF; font-size: 10px; background: transparent;")

    def _on_heatmap(self, data):
        heatmap, bss, ues = data
        fig = plt_utils.plot_sinr_heatmap(
            heatmap, bss, ues,
            area_size=self.params.get("area_size_m", 1000.0)
        )
        self.heatmap_canvas.set_figure(fig)

    def _on_topology(self, data):
        bss, ues, area = data
        fig = plt_utils.plot_network_topology(bss, ues, area)
        self.topo_canvas.set_figure(fig)

    def _on_kpis(self, kpis: dict):
        self.state.setdefault("kpis", {}).update(kpis)
        text = (
            f"<b style='color:#00D4FF'>Average SINR:</b>  {kpis.get('avg_sinr', 0):.2f} dB<br><br>"
            f"<b style='color:#7B2FFF'>Total Handovers:</b>  {kpis.get('handoff_count', 0)}<br><br>"
            f"<b style='color:#00FF88'>Active Users:</b>  {kpis.get('active_users', 0)} UEs<br><br>"
            f"<b style='color:#FFB800'>Cell Load:</b>  {kpis.get('cell_load', 0)*100:.1f}%<br><br>"
            f"<b style='color:#FF4560'>Avg Throughput:</b>  {kpis.get('avg_throughput', 0):.3f} Mbps<br>"
        )
        self.kpi_display.setText(text)

    def _on_done(self):
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress.setVisible(False)
        self.state["running"] = False

    def update_params(self, params: dict):
        self.params.update(params)
