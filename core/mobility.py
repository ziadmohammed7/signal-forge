"""
Mobility Model: Random Waypoint
"""
import numpy as np


class UE:
    """User Equipment entity."""
    def __init__(self, ue_id: int, x: float, y: float, speed: float = 5.0):
        self.id = ue_id
        self.x = x
        self.y = y
        self.speed = speed  # m/s
        self.target_x = x
        self.target_y = y
        self.serving_cell = None
        self.sinr = -999.0
        self.handover_count = 0
        self.throughput = 0.0

    def position(self):
        return np.array([self.x, self.y])


class RandomWaypointMobility:
    """Random Waypoint mobility model."""
    def __init__(self, area_size: float = 1000.0, speed_range=(1, 15), pause_time=2.0):
        self.area_size = area_size
        self.speed_min, self.speed_max = speed_range
        self.pause_time = pause_time
        self.ues = []
        self._targets = {}
        self._pauses = {}

    def add_ue(self, ue: UE):
        self.ues.append(ue)
        self._new_target(ue)
        self._pauses[ue.id] = 0.0

    def _new_target(self, ue: UE):
        self._targets[ue.id] = (
            np.random.uniform(0, self.area_size),
            np.random.uniform(0, self.area_size)
        )
        ue.speed = np.random.uniform(self.speed_min, self.speed_max)

    def step(self, dt: float = 1.0):
        """Advance mobility model by dt seconds."""
        for ue in self.ues:
            if self._pauses[ue.id] > 0:
                self._pauses[ue.id] -= dt
                continue
            tx, ty = self._targets[ue.id]
            dx = tx - ue.x
            dy = ty - ue.y
            dist = np.sqrt(dx**2 + dy**2)
            step = ue.speed * dt
            if dist <= step:
                ue.x, ue.y = tx, ty
                self._pauses[ue.id] = self.pause_time
                self._new_target(ue)
            else:
                ue.x += dx / dist * step
                ue.y += dy / dist * step
            # Clamp to area
            ue.x = np.clip(ue.x, 0, self.area_size)
            ue.y = np.clip(ue.y, 0, self.area_size)
