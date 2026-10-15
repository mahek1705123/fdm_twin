"""Read-only access to the measured/FEA design rows used for confidence and the explorer."""
import math

from ..domain.constants import MATERIALS, TOPOLOGIES
from ..domain.entities import DesignInput

TOPO, MAT = list(TOPOLOGIES), list(MATERIALS)


class DatasetRepository:
    def __init__(self, store):
        self._store = store

    def rows(self):
        return self._store.rows

    def nearest(self, d: DesignInput):
        """Closest row with the same topology and material, in a normalised design space."""
        best, best_d = None, 9.0
        for r in self.rows():
            if TOPO[r[0]] != d.topology or MAT[r[1]] != d.material:
                continue
            dist = math.hypot((r[2] - d.cell_size) / 20, (r[3] - d.wall_thickness) / 1, (r[4] - d.angle) / 20,
                              (r[5] - d.layer_thickness) / .2, (r[6] - d.nozzle_temp) / 40)
            if dist < best_d:
                best, best_d = r, dist
        return best, best_d
