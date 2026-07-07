"""
Channel Models: AWGN, Rayleigh Fading, Rician Fading
"""
import numpy as np


def add_noise(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """Add AWGN noise to signal."""
    snr_lin = 10 ** (snr_db / 10)
    sig_power = np.mean(np.abs(signal)**2)
    noise_power = sig_power / snr_lin
    noise = np.sqrt(noise_power / 2) * (np.random.randn(*signal.shape) + 1j * np.random.randn(*signal.shape))
    return signal + noise


def apply_rayleigh(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """Apply Rayleigh fading channel."""
    h = (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal))) / np.sqrt(2)
    faded = h * signal
    snr_lin = 10 ** (snr_db / 10)
    sig_power = np.mean(np.abs(faded)**2)
    noise_power = sig_power / snr_lin
    noise = np.sqrt(noise_power / 2) * (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal)))
    rx = faded + noise
    # Equalize
    rx = rx / (h + 1e-10)
    return rx


def apply_rician(signal: np.ndarray, snr_db: float, K_factor: float = 3.0) -> np.ndarray:
    """Apply Rician fading channel."""
    K = K_factor
    los = np.sqrt(K / (K + 1))
    scatter = np.sqrt(1 / (K + 1))
    h_scatter = scatter * (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal))) / np.sqrt(2)
    h = los + h_scatter
    faded = h * signal
    snr_lin = 10 ** (snr_db / 10)
    sig_power = np.mean(np.abs(faded)**2)
    noise_power = sig_power / snr_lin
    noise = np.sqrt(noise_power / 2) * (np.random.randn(len(signal)) + 1j * np.random.randn(len(signal)))
    rx = faded + noise
    rx = rx / (h + 1e-10)
    return rx


def path_loss_db(distance_m: float, freq_hz: float, exponent: float = 3.5) -> float:
    """Compute path loss in dB."""
    if distance_m < 1:
        distance_m = 1
    c = 3e8
    lambda_ = c / freq_hz
    pl_free = 20 * np.log10(4 * np.pi / lambda_)
    pl = pl_free + 10 * exponent * np.log10(distance_m)
    return pl


def received_power_dbm(tx_power_dbm: float, distance_m: float, freq_hz: float,
                        exponent: float = 3.5, shadow_std: float = 8.0) -> float:
    """Compute received power with path loss and shadowing."""
    pl = path_loss_db(distance_m, freq_hz, exponent)
    shadow = np.random.randn() * shadow_std
    return tx_power_dbm - pl + shadow


def noise_power_dbm(bandwidth_hz: float, noise_figure_db: float = 5.0) -> float:
    """Compute thermal noise power in dBm."""
    kT = -174  # dBm/Hz at room temp
    return kT + 10 * np.log10(bandwidth_hz) + noise_figure_db


def compute_sinr(signal_power_dbm: float, interference_powers_dbm: list,
                  noise_power_dbm_val: float) -> float:
    """Compute SINR in dB."""
    signal_lin = 10 ** (signal_power_dbm / 10)
    noise_lin = 10 ** (noise_power_dbm_val / 10)
    interf_lin = sum(10 ** (p / 10) for p in interference_powers_dbm)
    sinr_lin = signal_lin / (noise_lin + interf_lin + 1e-15)
    return 10 * np.log10(sinr_lin)
