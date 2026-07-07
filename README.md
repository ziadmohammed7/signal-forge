# Mobile Communication System Simulator

> A professional desktop simulation platform for cellular network analysis, built in Python + PySide6.

---

## Features

| Tab | Description |
|-----|-------------|
| 🏠 Dashboard | Live KPI cards, animated system diagram, status indicators |
| ⚙️ Parameters | Full RF + network + 5G parameter configuration with validation |
| 📡 TX / RX | Bit generator → modulator → channel → demodulator chain with live plots |
| 🌊 Channel | Real-time AWGN / Rayleigh / Rician channel visualizer with SNR slider |
| 📈 Results | BER vs SNR, constellation diagram, FFT spectrum, Shannon throughput |
| 🔍 Compare | Multi-scheme BER comparison on a single graph with stats |
| 🗺️ Network | Multi-cell SINR heatmap, A3 handover simulation, PF scheduler, UE mobility |
| 5G NR | Numerology selector, resource block grid, animated beamforming visualizer |
| 🤖 AI Model | Logistic regression handover predictor with training, confusion matrix, live inference |
| 📄 Report | One-click professional PDF report with plots, KPIs, and parameters |

---

## Installation

### Requirements
- Python 3.11+
- See `requirements.txt`

### Setup

```bash
# Clone / extract the project
cd mobile_comm_sim

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## Project Structure

```
mobile_comm_sim/
├── main.py                     # Entry point (splash screen + app launch)
├── requirements.txt
│
├── core/                       # Signal processing & network logic
│   ├── modulation.py           # BPSK, QPSK, 8PSK, 16QAM mod/demod + BER
│   ├── channel_models.py       # AWGN, Rayleigh, Rician; path loss; noise
│   ├── sinr.py                 # SINR computation, heatmap, BaseStation class
│   ├── mobility.py             # Random Waypoint mobility model + UE class
│   ├── handover.py             # A3 handover event logic + stats
│   ├── scheduler.py            # Proportional Fair resource scheduler
│   └── ai_model.py             # Logistic regression handover predictor
│
├── gui/                        # PySide6 GUI components
│   ├── styles.py               # Global dark theme stylesheet
│   ├── widgets.py              # KPICard, MatplotlibCanvas, StatusLED, etc.
│   ├── main_window.py          # Main tabbed application window
│   ├── dashboard_tab.py        # Hero banner + KPI cards + system diagram
│   ├── parameter_tab.py        # Configuration forms
│   ├── tx_rx_tab.py            # TX/RX chain + waveform + constellation
│   ├── channel_tab.py          # Live channel simulation viewer
│   ├── results_tab.py          # BER/SNR + FFT + throughput plots
│   ├── comparison_tab.py       # Multi-scheme BER comparison
│   ├── analysis_tab.py         # Multi-cell network + SINR heatmap
│   ├── fiveg_tab.py            # 5G NR numerology + RB grid + beamforming
│   ├── ai_tab.py               # AI handover prediction + training UI
│   └── report_tab.py           # PDF report generator
│
└── utils/
    ├── plotting.py             # Matplotlib figure builders (dark theme)
    └── pdf_report.py           # ReportLab PDF generation
```

---

## GitHub Repository Setup

Recommended repository name:

```text
mobile-communication-system-simulator
```

First upload:

```bash
git init
git add .
git commit -m "Initial commit: mobile communication simulator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mobile-communication-system-simulator.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## PyInstaller Build

```bash
pip install pyinstaller

pyinstaller mobile_comm_sim.spec
# or directly:
pyinstaller --onefile --windowed --name "CommSim" main.py
```

---

## Technical Details

### Modulation Schemes
| Scheme | Bits/Symbol | BER @ SNR=10dB (AWGN) |
|--------|------------|----------------------|
| BPSK   | 1          | ~0.5 × 10⁻³ |
| QPSK   | 2          | ~10⁻³ |
| 8PSK   | 3          | ~10⁻² |
| 16QAM  | 4          | ~3 × 10⁻² |

### Network Simulation
- **Cells**: Configurable 1–12 base stations in grid layout
- **Users**: Up to 50 UEs with Random Waypoint mobility
- **SINR**: Full inter-cell interference modeling with path loss + shadowing
- **Handover**: A3 event trigger with configurable hysteresis and TTT
- **Scheduler**: Proportional Fair with per-UE throughput tracking

### 5G NR Numerology
| μ | SCS | Slot Duration | RBs (10 MHz) |
|---|-----|---------------|--------------|
| 0 | 15 kHz | 1.0 ms | 52 |
| 1 | 30 kHz | 0.5 ms | 24 |
| 2 | 60 kHz | 0.25 ms | 11 |

---

## License
Graduation Project — Educational Use
