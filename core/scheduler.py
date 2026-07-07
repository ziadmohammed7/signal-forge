"""
Proportional Fair Scheduler (LTE-like)
"""
import numpy as np


class ProportionalFairScheduler:
    """
    PF scheduler: maximizes sum of log(throughput).
    Allocates resource blocks to UEs.
    """
    def __init__(self, n_resource_blocks: int = 25, alpha: float = 0.9):
        self.n_rb = n_resource_blocks
        self.alpha = alpha  # history weight
        self._avg_throughput = {}  # ue_id -> avg throughput

    def schedule(self, ues: list, sinr_fn) -> dict:
        """
        Returns dict: ue_id -> allocated_rbs
        """
        if not ues:
            return {}

        # Compute instantaneous rates
        inst_rates = {}
        for ue in ues:
            sinr = ue.sinr if ue.sinr > -100 else -100
            sinr_lin = 10 ** (sinr / 10)
            # Shannon per RB (180 kHz per RB)
            rate = 180e3 * np.log2(1 + sinr_lin)
            inst_rates[ue.id] = rate

            if ue.id not in self._avg_throughput:
                self._avg_throughput[ue.id] = max(rate, 1e3)

        # PF metric = instantaneous_rate / average_throughput
        metrics = {}
        for ue in ues:
            metrics[ue.id] = inst_rates[ue.id] / max(self._avg_throughput[ue.id], 1.0)

        # Sort by PF metric (descending)
        sorted_ues = sorted(ues, key=lambda u: metrics[u.id], reverse=True)

        # Allocate RBs round-robin among top UEs
        allocation = {ue.id: 0 for ue in ues}
        rb_per_ue = max(1, self.n_rb // len(ues))

        for i, ue in enumerate(sorted_ues):
            if i < self.n_rb:
                allocation[ue.id] = min(rb_per_ue, self.n_rb - sum(allocation.values()))

        # Distribute remaining
        remaining = self.n_rb - sum(allocation.values())
        for ue in sorted_ues:
            if remaining <= 0:
                break
            allocation[ue.id] += 1
            remaining -= 1

        # Update average throughput
        for ue in ues:
            current = inst_rates[ue.id] * allocation[ue.id] / self.n_rb
            self._avg_throughput[ue.id] = (
                self.alpha * self._avg_throughput[ue.id] +
                (1 - self.alpha) * current
            )
            ue.throughput = current / 1e6  # Mbps

        return allocation

    def get_cell_load(self, bs_id: int, ues: list) -> float:
        """Fraction of RBs used."""
        n_ues = sum(1 for ue in ues if ue.serving_cell == bs_id)
        return min(n_ues * (self.n_rb // max(len(ues), 1)) / self.n_rb, 1.0)
