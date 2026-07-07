"""
Modulation and Demodulation Module
Supports: BPSK, QPSK, 8PSK, 16QAM
"""
import numpy as np


def generate_bits(n_bits: int) -> np.ndarray:
    """Generate random bit stream."""
    return np.random.randint(0, 2, n_bits)


def modulate(bits: np.ndarray, scheme: str) -> np.ndarray:
    """Modulate bits using the specified scheme."""
    scheme = scheme.upper()
    if scheme == "BPSK":
        return _bpsk_mod(bits)
    elif scheme == "QPSK":
        return _qpsk_mod(bits)
    elif scheme == "8PSK":
        return _8psk_mod(bits)
    elif scheme == "16QAM":
        return _16qam_mod(bits)
    else:
        raise ValueError(f"Unknown modulation scheme: {scheme}")


def demodulate(symbols: np.ndarray, scheme: str) -> np.ndarray:
    """Demodulate symbols to bits."""
    scheme = scheme.upper()
    if scheme == "BPSK":
        return _bpsk_demod(symbols)
    elif scheme == "QPSK":
        return _qpsk_demod(symbols)
    elif scheme == "8PSK":
        return _8psk_demod(symbols)
    elif scheme == "16QAM":
        return _16qam_demod(symbols)
    else:
        raise ValueError(f"Unknown modulation scheme: {scheme}")


def bits_per_symbol(scheme: str) -> int:
    mapping = {"BPSK": 1, "QPSK": 2, "8PSK": 3, "16QAM": 4}
    return mapping.get(scheme.upper(), 1)


def get_constellation(scheme: str) -> np.ndarray:
    """Return ideal constellation points."""
    scheme = scheme.upper()
    if scheme == "BPSK":
        return np.array([-1+0j, 1+0j])
    elif scheme == "QPSK":
        angles = np.pi/4 + np.arange(4) * np.pi/2
        return np.exp(1j * angles)
    elif scheme == "8PSK":
        angles = np.arange(8) * 2*np.pi/8
        return np.exp(1j * angles)
    elif scheme == "16QAM":
        pts = []
        for i in [-3, -1, 1, 3]:
            for q in [-3, -1, 1, 3]:
                pts.append(complex(i, q))
        return np.array(pts) / np.sqrt(10)
    return np.array([])


# --- BPSK ---
def _bpsk_mod(bits):
    return (2*bits - 1).astype(complex)


def _bpsk_demod(symbols):
    return (symbols.real > 0).astype(int)


# --- QPSK ---
# Natural binary mapping: b0 controls real polarity, b1 controls imag polarity
# (0,0)->+I+Q  (0,1)->+I-Q  (1,0)->-I+Q  (1,1)->-I-Q
def _qpsk_mod(bits):
    bits = bits[:len(bits) - len(bits) % 2]
    pairs = bits.reshape(-1, 2)
    I = np.where(pairs[:, 0] == 0, 1.0, -1.0)
    Q = np.where(pairs[:, 1] == 0, 1.0, -1.0)
    return (I + 1j * Q) / np.sqrt(2)


def _qpsk_demod(symbols):
    b0 = (symbols.real < 0).astype(int)
    b1 = (symbols.imag < 0).astype(int)
    bits = np.empty(len(symbols) * 2, dtype=int)
    bits[0::2] = b0
    bits[1::2] = b1
    return bits


# --- 8PSK ---
def _8psk_mod(bits):
    n = len(bits) - len(bits)%3
    bits = bits[:n].reshape(-1, 3)
    indices = bits[:,0]*4 + bits[:,1]*2 + bits[:,2]
    angles = indices * 2*np.pi/8
    return np.exp(1j * angles)


def _8psk_demod(symbols):
    angles = np.angle(symbols) % (2*np.pi)
    indices = np.round(angles * 8 / (2*np.pi)).astype(int) % 8
    bits = []
    for idx in indices:
        bits.extend([(idx>>2)&1, (idx>>1)&1, idx&1])
    return np.array(bits)


# --- 16QAM ---
def _16qam_mod(bits):
    n = len(bits) - len(bits)%4
    bits = bits[:n].reshape(-1, 4)
    gray_map = [0, 1, 3, 2]
    amp = [-3, -1, 1, 3]
    I_idx = bits[:,0]*2 + bits[:,1]
    Q_idx = bits[:,2]*2 + bits[:,3]
    I_vals = np.array([amp[gray_map[i]] for i in I_idx])
    Q_vals = np.array([amp[gray_map[i]] for i in Q_idx])
    return (I_vals + 1j*Q_vals) / np.sqrt(10)


def _16qam_demod(symbols):
    symbols = symbols * np.sqrt(10)
    amp_levels = np.array([-3, -1, 1, 3])
    gray_map = [0, 1, 3, 2]
    bits = []
    for s in symbols:
        I = s.real
        Q = s.imag
        I_idx = np.argmin(np.abs(amp_levels - I))
        Q_idx = np.argmin(np.abs(amp_levels - Q))
        I_gray = gray_map[I_idx]
        Q_gray = gray_map[Q_idx]
        bits.extend([(I_gray>>1)&1, I_gray&1, (Q_gray>>1)&1, Q_gray&1])
    return np.array(bits)


def compute_ber(snr_db_range, scheme: str, channel: str = "AWGN", n_bits: int = 50000):
    """Compute BER vs SNR for a given modulation and channel."""
    from core.channel_models import add_noise, apply_rayleigh, apply_rician
    ber_list = []
    bps = bits_per_symbol(scheme)
    for snr_db in snr_db_range:
        bits = generate_bits(n_bits)
        syms = modulate(bits, scheme)
        snr_lin = 10**(snr_db/10)
        if channel == "AWGN":
            rx = add_noise(syms, snr_db)
        elif channel == "Rayleigh":
            rx = apply_rayleigh(syms, snr_db)
        elif channel == "Rician":
            rx = apply_rician(syms, snr_db)
        else:
            rx = add_noise(syms, snr_db)
        rx_bits = demodulate(rx, scheme)
        n = min(len(bits), len(rx_bits))
        ber = np.mean(bits[:n] != rx_bits[:n])
        ber_list.append(max(ber, 1e-7))
    return np.array(ber_list)
