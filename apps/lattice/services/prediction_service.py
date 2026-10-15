"""Use-cases around the surrogate: predict, compare topologies, sweep one input."""
import numpy as np
import pandas as pd

from ..domain.constants import ANGLES, RANGES, TARGETS, TOPOLOGIES
from ..domain.entities import DesignInput, DomainError

SWEEPABLE = {"cell_size", "wall_thickness", "nozzle_temp"}


def confidence(distance: float) -> dict:
    if distance < .12:
        label, level = "High", "ok"
    elif distance < .30:
        label, level = "Medium", "mid"
    else:
        label, level = "Low (extrapolating)", "low"
    return {"label": label, "level": level, "distance": round(distance, 3)}


class PredictionService:
    def __init__(self, store, dataset):
        self.store, self.dataset = store, dataset

    def predict(self, d: DesignInput) -> dict:
        pred = self.store.predict(pd.DataFrame([d.as_row()]))
        values = {k: float(v[0]) for k, v in pred.items()}
        row, dist = self.dataset.nearest(d)
        nearest = None
        if row:
            nearest = {"topology": TOPOLOGIES[list(TOPOLOGIES)[row[0]]], "cell_size": row[2], "wall_thickness": row[3],
                       "E": row[7], "NU": row[10], "SEA": row[11],
                       "E_diff_pct": round((values["E"] / row[7] - 1) * 100, 1)}
        return {"values": values, "nearest": nearest, "confidence": confidence(dist)}

    def compare_topologies(self, d: DesignInput, metric: str) -> list[dict]:
        self._check_metric(metric)
        variants = [d.with_(topology=t, angle=d.angle if d.angle in ANGLES[t] else ANGLES[t][0]) for t in TOPOLOGIES]
        frame = pd.DataFrame([v.as_row() for v in variants])
        vals = self.store.predict(frame, [metric])[metric]
        return [{"topology": v.topology, "label": TOPOLOGIES[v.topology], "value": float(x),
                 "selected": v.topology == d.topology} for v, x in zip(variants, vals)]

    def sensitivity(self, d: DesignInput, variable: str, metric: str) -> dict:
        self._check_metric(metric)
        if variable not in SWEEPABLE:
            raise DomainError(f"variable must be one of {sorted(SWEEPABLE)}")
        lo, hi, _ = RANGES[variable]
        xs = np.linspace(lo, hi, 41)
        frame = pd.DataFrame([d.with_(**{variable: float(x)}).as_row() for x in xs])
        ys = self.store.predict(frame, [metric])[metric]
        return {"variable": variable, "current": getattr(d, variable),
                "points": [[round(float(x), 3), float(y)] for x, y in zip(xs, ys)]}

    @staticmethod
    def _check_metric(m):
        if m not in TARGETS:
            raise DomainError(f"metric must be one of {list(TARGETS)}")
