"""
A3 Handover Logic (LTE-like)
"""
import numpy as np


class A3HandoverManager:
    """
    Implements A3 event-based handover:
    Trigger when: SINR(target) - SINR(serving) > hysteresis for time_to_trigger
    """
    def __init__(self, hysteresis_db: float = 3.0, time_to_trigger: float = 0.5,
                 offset_db: float = 0.0):
        self.hysteresis_db = hysteresis_db
        self.time_to_trigger = time_to_trigger
        self.offset_db = offset_db
        self._candidates = {}  # ue_id -> (target_bs_id, elapsed_time)

    def evaluate(self, ue, base_stations: list, sinr_fn, dt: float = 1.0) -> int | None:
        """
        Evaluate handover decision.
        Returns new serving BS ID if handover triggered, else None.
        """
        serving_id = ue.serving_cell
        # Compute SINR for all cells
        sinr_vals = {}
        for bs in base_stations:
            sinr_vals[bs.id] = sinr_fn(bs.id, ue.x, ue.y)

        serving_sinr = sinr_vals.get(serving_id, -999.0)

        # Find best candidate
        best_id = serving_id
        best_sinr = serving_sinr
        for bs_id, sinr in sinr_vals.items():
            if sinr > best_sinr:
                best_sinr = sinr
                best_id = bs_id

        if best_id == serving_id:
            # No better cell, clear any candidate
            self._candidates.pop(ue.id, None)
            return None

        # Check A3 condition: target SINR - serving SINR > hysteresis
        diff = best_sinr - serving_sinr
        if diff >= self.hysteresis_db + self.offset_db:
            # Start or continue TTT
            if ue.id in self._candidates and self._candidates[ue.id][0] == best_id:
                elapsed = self._candidates[ue.id][1] + dt
                self._candidates[ue.id] = (best_id, elapsed)
                if elapsed >= self.time_to_trigger:
                    del self._candidates[ue.id]
                    return best_id
            else:
                self._candidates[ue.id] = (best_id, 0.0)
        else:
            self._candidates.pop(ue.id, None)
        return None


class HandoverStats:
    """Track handover statistics."""
    def __init__(self):
        self.total_handovers = 0
        self.handover_log = []  # (time, ue_id, from_bs, to_bs)

    def record(self, time: float, ue_id: int, from_bs: int, to_bs: int):
        self.total_handovers += 1
        self.handover_log.append((time, ue_id, from_bs, to_bs))

    def recent_rate(self, window: float = 10.0, current_time: float = 0.0) -> float:
        """Handovers per second in recent window."""
        recent = [e for e in self.handover_log if current_time - e[0] <= window]
        return len(recent) / window if window > 0 else 0.0
