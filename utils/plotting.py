"""
Plotting utilities for the simulator.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

DARK_BG = "#0A0E1A"
PANEL_BG = "#0F1629"
ACCENT = "#00D4FF"
ACCENT2 = "#7B2FFF"
GRID_COLOR = "#1A2040"
TEXT_COLOR = "#C8D6F0"


def dark_figure(figsize=(8, 4), nrows=1, ncols=1):
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, facecolor=DARK_BG)
    if nrows == 1 and ncols == 1:
        axes = [axes]
    elif nrows == 1 or ncols == 1:
        axes = list(axes)
    else:
        axes = [ax for row in axes for ax in row]
    for ax in axes:
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_COLOR, labelsize=8)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(TEXT_COLOR)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_COLOR)
        ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7)
    return fig, axes


def plot_ber_vs_snr(snr_range, ber_dict: dict, title="BER vs SNR") -> Figure:
    """Plot BER vs SNR curves for multiple modulation schemes."""
    colors = [ACCENT, "#FF6B6B", "#F0E040", "#7B2FFF", "#00FF88"]
    fig, (ax,) = dark_figure(figsize=(8, 5))
    for i, (scheme, ber) in enumerate(ber_dict.items()):
        color = colors[i % len(colors)]
        ax.semilogy(snr_range, ber, '-o', markersize=3, label=scheme,
                    color=color, linewidth=1.8)
    ax.set_xlabel("SNR (dB)", color=TEXT_COLOR)
    ax.set_ylabel("Bit Error Rate", color=TEXT_COLOR)
    ax.set_title(title, color=TEXT_COLOR, fontsize=11, fontweight='bold')
    ax.legend(facecolor="#0F1629", edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=8)
    ax.set_ylim(bottom=1e-6)
    fig.tight_layout()
    return fig


def plot_constellation(symbols: np.ndarray, scheme: str,
                        ideal_symbols: np.ndarray = None) -> Figure:
    """Plot constellation diagram."""
    fig, (ax,) = dark_figure(figsize=(5, 5))
    ax.scatter(symbols.real, symbols.imag, s=4, alpha=0.4, color=ACCENT, label="Received")
    if ideal_symbols is not None:
        ax.scatter(ideal_symbols.real, ideal_symbols.imag, s=80, color="#FF6B6B",
                   marker='*', zorder=5, label="Ideal")
    ax.set_xlabel("In-Phase (I)", color=TEXT_COLOR)
    ax.set_ylabel("Quadrature (Q)", color=TEXT_COLOR)
    ax.set_title(f"{scheme} Constellation", color=TEXT_COLOR, fontsize=11, fontweight='bold')
    ax.axhline(0, color=GRID_COLOR, linewidth=0.8)
    ax.axvline(0, color=GRID_COLOR, linewidth=0.8)
    ax.legend(facecolor="#0F1629", edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, fontsize=8)
    ax.set_aspect('equal')
    fig.tight_layout()
    return fig


def plot_waveform(signal: np.ndarray, title="Signal Waveform", n_samples=200) -> Figure:
    """Plot signal waveform (real part)."""
    fig, (ax,) = dark_figure(figsize=(8, 3))
    t = np.arange(min(n_samples, len(signal)))
    ax.plot(t, signal[:len(t)].real, color=ACCENT, linewidth=1.2)
    ax.fill_between(t, signal[:len(t)].real, alpha=0.15, color=ACCENT)
    ax.set_xlabel("Sample", color=TEXT_COLOR)
    ax.set_ylabel("Amplitude", color=TEXT_COLOR)
    ax.set_title(title, color=TEXT_COLOR, fontsize=10, fontweight='bold')
    fig.tight_layout()
    return fig


def plot_fft_spectrum(signal: np.ndarray, fs: float = 1.0, title="FFT Spectrum") -> Figure:
    """Plot FFT power spectrum."""
    N = len(signal)
    spectrum = np.fft.fftshift(np.fft.fft(signal, N))
    freqs = np.fft.fftshift(np.fft.fftfreq(N, 1/fs))
    power_db = 20 * np.log10(np.abs(spectrum) / N + 1e-12)
    fig, (ax,) = dark_figure(figsize=(8, 3))
    ax.plot(freqs, power_db, color=ACCENT2, linewidth=1.2)
    ax.fill_between(freqs, power_db, power_db.min(), alpha=0.2, color=ACCENT2)
    ax.set_xlabel("Frequency (normalized)", color=TEXT_COLOR)
    ax.set_ylabel("Power (dB)", color=TEXT_COLOR)
    ax.set_title(title, color=TEXT_COLOR, fontsize=10, fontweight='bold')
    fig.tight_layout()
    return fig


def plot_sinr_heatmap(heatmap: np.ndarray, base_stations: list,
                       ues: list = None, area_size: float = 1000.0) -> Figure:
    """Plot SINR heatmap with BS and UE positions."""
    fig, (ax,) = dark_figure(figsize=(8, 7))
    im = ax.imshow(heatmap, origin='lower', extent=[0, area_size, 0, area_size],
                   cmap='RdYlGn', vmin=-10, vmax=30, alpha=0.85)
    plt.colorbar(im, ax=ax, label='SINR (dB)', shrink=0.8)

    # Plot base stations
    for bs in base_stations:
        ax.plot(bs.x, bs.y, '^', color='#FFD700', markersize=12,
                markeredgecolor='white', markeredgewidth=0.8, zorder=5)
        ax.annotate(f'BS{bs.id}', (bs.x, bs.y), textcoords='offset points',
                    xytext=(5, 5), color='white', fontsize=7, fontweight='bold')
        # Draw sectors
        for angle in bs.sectors:
            rad = np.radians(angle)
            ax.annotate('', xy=(bs.x + 80*np.cos(rad), bs.y + 80*np.sin(rad)),
                        xytext=(bs.x, bs.y),
                        arrowprops=dict(arrowstyle='->', color='#FFD700', lw=1.2))

    # Plot UEs
    if ues:
        for ue in ues:
            color = '#00D4FF' if ue.serving_cell is not None else '#FF6B6B'
            ax.plot(ue.x, ue.y, 'o', color=color, markersize=6,
                    markeredgecolor='white', markeredgewidth=0.5, zorder=6)
            ax.annotate(f'U{ue.id}', (ue.x, ue.y), textcoords='offset points',
                        xytext=(3, 3), color='#C8D6F0', fontsize=6)

    ax.set_xlabel("X (m)", color=TEXT_COLOR)
    ax.set_ylabel("Y (m)", color=TEXT_COLOR)
    ax.set_title("SINR Heatmap", color=TEXT_COLOR, fontsize=11, fontweight='bold')
    fig.tight_layout()
    return fig


def plot_network_topology(base_stations: list, ues: list,
                           area_size: float = 1000.0) -> Figure:
    """Plot interactive network topology."""
    fig, (ax,) = dark_figure(figsize=(8, 7))
    ax.set_xlim(0, area_size)
    ax.set_ylim(0, area_size)

    # Coverage circles
    bs_colors = ['#00D4FF', '#FF6B6B', '#00FF88', '#F0E040', '#FF8800', '#CC00FF']
    for i, bs in enumerate(base_stations):
        color = bs_colors[i % len(bs_colors)]
        circle = plt.Circle((bs.x, bs.y), area_size * 0.2, color=color,
                              fill=True, alpha=0.08, linestyle='--', linewidth=1)
        ax.add_patch(circle)
        ax.plot(bs.x, bs.y, '^', color=color, markersize=14,
                markeredgecolor='white', markeredgewidth=1, zorder=5, label=f'BS {bs.id}')

    # UEs and connections
    for ue in ues:
        ax.plot(ue.x, ue.y, 'o', color='white', markersize=5, zorder=6)
        if ue.serving_cell is not None:
            # Draw line to serving BS
            serving = next((bs for bs in base_stations if bs.id == ue.serving_cell), None)
            if serving:
                color = bs_colors[base_stations.index(serving) % len(bs_colors)]
                ax.plot([ue.x, serving.x], [ue.y, serving.y],
                        '-', color=color, alpha=0.3, linewidth=0.8)

    ax.set_xlabel("X (m)", color=TEXT_COLOR)
    ax.set_ylabel("Y (m)", color=TEXT_COLOR)
    ax.set_title("Network Topology", color=TEXT_COLOR, fontsize=11, fontweight='bold')
    ax.legend(facecolor="#0F1629", edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR,
               fontsize=7, loc='upper right')
    fig.tight_layout()
    return fig


def figure_to_pixmap(fig: Figure):
    """Convert matplotlib figure to QPixmap."""
    from io import BytesIO
    from PySide6.QtGui import QPixmap, QImage
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    buf.seek(0)
    img = QImage.fromData(buf.getvalue())
    return QPixmap.fromImage(img)
