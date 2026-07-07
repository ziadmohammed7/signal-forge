"""
SINR computation for multi-cell network simulation.
"""
import numpy as np
from core.channel_models import path_loss_db, noise_power_dbm


class BaseStation:
    """Base station with 3 sectors."""
    def __init__(self, bs_id: int, x: float, y: float,
                 tx_power_dbm: float = 43.0,
                 freq_hz: float = 2.1e9,
                 bandwidth_hz: float = 10e6,
                 noise_figure_db: float = 5.0,
                 path_loss_exp: float = 3.5):
        self.id = bs_id
        self.x = x
        self.y = y
        self.tx_power_dbm = tx_power_dbm
        self.freq_hz = freq_hz
        self.bandwidth_hz = bandwidth_hz
        self.noise_figure_db = noise_figure_db
        self.path_loss_exp = path_loss_exp
        self.sectors = [0, 120, 240]  # degrees
        self.connected_ues = []
        self.load = 0.0

    def position(self):
        return np.array([self.x, self.y])

    def received_power_dbm(self, ue_x: float, ue_y: float) -> float:
        dist = np.sqrt((ue_x - self.x)**2 + (ue_y - self.y)**2)
        dist = max(dist, 1.0)
        pl = path_loss_db(dist, self.freq_hz, self.path_loss_exp)
        return self.tx_power_dbm - pl

    def sector_gain_db(self, ue_x: float, ue_y: float, sector_angle: float) -> float:
        """Antenna gain based on sector direction (simplified)."""
        dx = ue_x - self.x
        dy = ue_y - self.y
        angle = np.degrees(np.arctan2(dy, dx)) % 360
        delta = abs(angle - sector_angle)
        delta = min(delta, 360 - delta)
        # 3GPP sector pattern: max 17 dBi, HPBW = 65 degrees
        Am = 20  # dB
        theta_3db = 65
        gain = -min(12 * (delta / theta_3db)**2, Am)
        return gain


def compute_network_sinr(base_stations: list, ue_x: float, ue_y: float,
                          serving_bs_id: int, noise_figure_db: float = 5.0,
                          bandwidth_hz: float = 10e6) -> float:
    """Compute SINR for a UE at given position."""
    noise = noise_power_dbm(bandwidth_hz, noise_figure_db)
    interference_powers = []
    signal_power = None

    for bs in base_stations:
        pwr = bs.received_power_dbm(ue_x, ue_y)
        if bs.id == serving_bs_id:
            signal_power = pwr
        else:
            interference_powers.append(pwr)

    if signal_power is None:
        return -999.0

    signal_lin = 10 ** (signal_power / 10)
    noise_lin = 10 ** (noise / 10)
    interf_lin = sum(10 ** (p / 10) for p in interference_powers)
    sinr = signal_lin / (noise_lin + interf_lin + 1e-15)
    return 10 * np.log10(sinr)


def find_best_cell(base_stations: list, ue_x: float, ue_y: float) -> int:
    """Find the base station with the highest received power."""
    best_id = None
    best_power = -np.inf
    for bs in base_stations:
        pwr = bs.received_power_dbm(ue_x, ue_y)
        if pwr > best_power:
            best_power = pwr
            best_id = bs.id
    return best_id


def compute_sinr_heatmap(base_stations: list, area_size: float = 1000.0,
                          resolution: int = 50, bandwidth_hz: float = 10e6,
                          noise_figure_db: float = 5.0) -> np.ndarray:
    """Compute SINR heatmap over the entire area."""
    xs = np.linspace(0, area_size, resolution)
    ys = np.linspace(0, area_size, resolution)
    heatmap = np.zeros((resolution, resolution))

    for i, y in enumerate(ys):
        for j, x in enumerate(xs):
            best = find_best_cell(base_stations, x, y)
            if best is not None:
                sinr = compute_network_sinr(
                    base_stations, x, y, best, noise_figure_db, bandwidth_hz
                )
                heatmap[i, j] = sinr
    return heatmap


def estimate_throughput_mbps(sinr_db: float, bandwidth_hz: float) -> float:
    """Estimate throughput using Shannon's formula."""
    sinr_lin = 10 ** (sinr_db / 10)
    capacity_bps = bandwidth_hz * np.log2(1 + sinr_lin)
    return capacity_bps / 1e6
