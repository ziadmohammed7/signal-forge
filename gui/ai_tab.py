"""
AI Handover Prediction Tab
"""
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                  QPushButton, QFrame, QGroupBox, QFormLayout,
                                  QDoubleSpinBox, QProgressBar, QTextEdit, QSlider)
from PySide6.QtCore import Qt, QThread, Signal
from gui.widgets import SectionHeader, MatplotlibCanvas
from core.ai_model import HandoverPredictor
import utils.plotting as plt_utils
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class AITrainWorker(QThread):
    progress = Signal(str)
    finished = Signal(object, dict)  # (predictor, metrics)

    def run(self):
        self.progress.emit("Generating synthetic training data...")
        pred = HandoverPredictor()
        n_samples = 500
        np.random.seed(42)
        sinr_serving = np.random.uniform(-10, 30, n_samples)
        sinr_best = sinr_serving + np.random.uniform(-5, 10, n_samples)
        dist_serving = np.random.uniform(50, 800, n_samples)
        dist_best = np.random.uniform(50, 800, n_samples)

        for i in range(n_samples):
            ho = (sinr_best[i] - sinr_serving[i] > 3.0) and (dist_best[i] < dist_serving[i])
            pred.record_sample(sinr_serving[i], sinr_best[i], dist_serving[i], dist_best[i], ho)

        self.progress.emit("Training logistic regression model...")
        success = pred.train()

        # Evaluate
        n_test = 200
        sinr_s = np.random.uniform(-5, 25, n_test)
        sinr_b = sinr_s + np.random.uniform(-5, 8, n_test)
        ds = np.random.uniform(50, 700, n_test)
        db = np.random.uniform(50, 700, n_test)
        y_true = ((sinr_b - sinr_s > 3.0) & (db < ds)).astype(int)
        y_pred = [int(pred.predict(sinr_s[i], sinr_b[i], ds[i], db[i])) for i in range(n_test)]
        acc = np.mean(np.array(y_true) == np.array(y_pred))

        self.progress.emit(f"Training complete. Accuracy: {acc*100:.1f}%")
        self.finished.emit(pred, {
            "accuracy": acc,
            "n_train": n_samples,
            "n_test": n_test,
            "success": success,
            "sinr_s_test": sinr_s,
            "sinr_b_test": sinr_b,
            "ds_test": ds,
            "db_test": db,
            "y_true": y_true,
            "y_pred": y_pred,
        })


class AITab(QWidget):
    """AI-based handover prediction tab."""

    def __init__(self, simulation_state: dict, parent=None):
        super().__init__(parent)
        self.state = simulation_state
        self._predictor = HandoverPredictor()
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(SectionHeader("AI-Based Handover Prediction"))

        # Description
        desc = QLabel(
            "The AI model uses logistic regression to predict handover probability "
            "based on SINR, SINR delta, and distance metrics. Train on synthetic data "
            "then test with custom inputs."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(
            "color: #8090B0; font-size: 10px; background: #0F1629; "
            "border: 1px solid #1A2A4A; border-radius: 6px; padding: 10px;"
        )
        layout.addWidget(desc)

        # Top row: train + predict
        row = QHBoxLayout()
        row.setSpacing(14)

        # Train panel
        train_grp = QGroupBox("Model Training")
        train_vl = QVBoxLayout(train_grp)
        train_vl.setSpacing(10)

        self.btn_train = QPushButton("🧠  Train Model")
        self.btn_train.setObjectName("primary")
        self.btn_train.setMinimumHeight(38)
        self.btn_train.clicked.connect(self._train)
        train_vl.addWidget(self.btn_train)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        train_vl.addWidget(self.progress)

        self.train_status = QLabel("Model not trained.")
        self.train_status.setStyleSheet("color: #8090B0; font-size: 10px; background: transparent;")
        self.train_status.setWordWrap(True)
        train_vl.addWidget(self.train_status)

        self.metrics_lbl = QLabel("")
        self.metrics_lbl.setStyleSheet(
            "color: #C8D6F0; font-size: 11px; background: transparent;"
        )
        self.metrics_lbl.setWordWrap(True)
        train_vl.addWidget(self.metrics_lbl)

        train_vl.addStretch()
        row.addWidget(train_grp)

        # Predict panel
        pred_grp = QGroupBox("Live Prediction")
        pred_form = QFormLayout(pred_grp)
        pred_form.setSpacing(10)

        self.w_sinr_s = QDoubleSpinBox()
        self.w_sinr_s.setRange(-20, 40)
        self.w_sinr_s.setValue(5.0)
        self.w_sinr_s.setSuffix(" dB")
        self.w_sinr_s.setToolTip("SINR of the currently serving cell")
        pred_form.addRow("SINR Serving:", self.w_sinr_s)

        self.w_sinr_b = QDoubleSpinBox()
        self.w_sinr_b.setRange(-20, 40)
        self.w_sinr_b.setValue(12.0)
        self.w_sinr_b.setSuffix(" dB")
        self.w_sinr_b.setToolTip("Best SINR from candidate cells")
        pred_form.addRow("SINR Best Cell:", self.w_sinr_b)

        self.w_dist_s = QDoubleSpinBox()
        self.w_dist_s.setRange(10, 2000)
        self.w_dist_s.setValue(400.0)
        self.w_dist_s.setSuffix(" m")
        self.w_dist_s.setToolTip("Distance to serving base station")
        pred_form.addRow("Dist to Serving:", self.w_dist_s)

        self.w_dist_b = QDoubleSpinBox()
        self.w_dist_b.setRange(10, 2000)
        self.w_dist_b.setValue(200.0)
        self.w_dist_b.setSuffix(" m")
        self.w_dist_b.setToolTip("Distance to best candidate base station")
        pred_form.addRow("Dist to Best:", self.w_dist_b)

        btn_predict = QPushButton("⚡  Predict Handover")
        btn_predict.setMinimumHeight(34)
        btn_predict.clicked.connect(self._predict)
        pred_form.addRow("", btn_predict)

        self.pred_result = QLabel("—")
        self.pred_result.setStyleSheet(
            "color: #E8F0FF; font-size: 18px; font-weight: 700; "
            "background: #0F1629; border: 1px solid #1A2A4A; "
            "border-radius: 6px; padding: 10px; text-align: center;"
        )
        self.pred_result.setAlignment(Qt.AlignCenter)
        pred_form.addRow("Result:", self.pred_result)

        row.addWidget(pred_grp)
        layout.addLayout(row)

        # Feature importance + confusion matrix canvas
        self.plot_canvas = MatplotlibCanvas()
        self.plot_canvas.setMinimumHeight(280)
        layout.addWidget(self.plot_canvas, 1)

    def _train(self):
        if self._worker and self._worker.isRunning():
            return
        self.btn_train.setEnabled(False)
        self.progress.setVisible(True)
        self.train_status.setText("Training...")
        self._worker = AITrainWorker()
        self._worker.progress.connect(self.train_status.setText)
        self._worker.finished.connect(self._on_trained)
        self._worker.start()

    def _on_trained(self, predictor, metrics):
        self._predictor = predictor
        self.btn_train.setEnabled(True)
        self.progress.setVisible(False)
        acc = metrics["accuracy"]
        self.train_status.setText(f"✓ Training complete")
        self.train_status.setStyleSheet("color: #00FF88; font-size: 10px; background: transparent;")
        self.metrics_lbl.setText(
            f"Accuracy: {acc*100:.1f}%\n"
            f"Train samples: {metrics['n_train']}\n"
            f"Test samples: {metrics['n_test']}"
        )
        self._plot_results(metrics)

    def _plot_results(self, metrics):
        y_true = metrics["y_true"]
        y_pred = metrics["y_pred"]
        importance = self._predictor.get_feature_importance()

        fig, axes = plt_utils.dark_figure(figsize=(10, 4), nrows=1, ncols=2)
        ax1, ax2 = axes

        # Confusion matrix
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_true, y_pred)
        im = ax1.imshow(cm, cmap='Blues', aspect='auto')
        ax1.set_xticks([0, 1])
        ax1.set_yticks([0, 1])
        ax1.set_xticklabels(["No HO", "HO"], color=plt_utils.TEXT_COLOR)
        ax1.set_yticklabels(["No HO", "HO"], color=plt_utils.TEXT_COLOR)
        ax1.set_xlabel("Predicted", color=plt_utils.TEXT_COLOR)
        ax1.set_ylabel("Actual", color=plt_utils.TEXT_COLOR)
        ax1.set_title("Confusion Matrix", color=plt_utils.TEXT_COLOR, fontweight='bold')
        for i in range(2):
            for j in range(2):
                ax1.text(j, i, str(cm[i, j]), ha='center', va='center',
                          color='white', fontsize=14, fontweight='bold')

        # Feature importance
        labels = [f[0] for f in importance]
        vals = [f[1] for f in importance]
        colors = ["#00D4FF", "#7B2FFF", "#00FF88", "#FFB800"]
        bars = ax2.barh(labels, vals, color=colors, alpha=0.85)
        ax2.set_xlabel("Importance (|weight|)", color=plt_utils.TEXT_COLOR)
        ax2.set_title("Feature Importance", color=plt_utils.TEXT_COLOR, fontweight='bold')
        ax2.tick_params(colors=plt_utils.TEXT_COLOR)

        fig.tight_layout()
        self.plot_canvas.set_figure(fig)

    def _predict(self):
        prob = self._predictor.predict_probability(
            self.w_sinr_s.value(), self.w_sinr_b.value(),
            self.w_dist_s.value(), self.w_dist_b.value()
        )
        ho = prob >= 0.5
        if ho:
            self.pred_result.setText(f"🔄 HANDOVER  ({prob*100:.1f}%)")
            self.pred_result.setStyleSheet(
                "color: #00D4FF; font-size: 16px; font-weight: 700; "
                "background: #0A1A30; border: 2px solid #00D4FF; "
                "border-radius: 6px; padding: 10px;"
            )
        else:
            self.pred_result.setText(f"📶 STAY  ({(1-prob)*100:.1f}%)")
            self.pred_result.setStyleSheet(
                "color: #00FF88; font-size: 16px; font-weight: 700; "
                "background: #0A1A10; border: 2px solid #00FF88; "
                "border-radius: 6px; padding: 10px;"
            )
