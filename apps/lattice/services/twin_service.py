"""Digital-twin use-cases: geometry, idealised response, ANSYS export and FEA cross-check."""
import pandas as pd

from ..domain import mechanics
from ..domain.constants import ANGLES, TOPOLOGIES
from ..domain.entities import DesignInput, DomainError
from ..domain.geometry import tile
from ..infrastructure import apdl


class TwinService:
    def __init__(self, store):
        self.store = store

    def _predict_one(self, d):
        return {k: float(v[0]) for k, v in self.store.predict(pd.DataFrame([d.as_row()])).items()}

    def geometry(self, d: DesignInput) -> dict:
        paths = [[[round(x, 4), round(y, 4)] for x, y in p] for p in tile(d.topology, d.angle, 4)]
        return {"paths": paths, "wall_ratio": d.wall_thickness / d.cell_size}

    def curves(self, d: DesignInput) -> dict:
        values = self._predict_one(d)
        variants = [d.with_(topology=t, angle=d.angle if d.angle in ANGLES[t] else ANGLES[t][0]) for t in TOPOLOGIES]
        pred = self.store.predict(pd.DataFrame([v.as_row() for v in variants]), ["E", "CPS"])
        series = [{"topology": v.topology, "label": TOPOLOGIES[v.topology], "selected": v.topology == d.topology,
                   "points": mechanics.curve(float(pred["E"][i]), float(pred["CPS"][i]))} for i, v in enumerate(variants)]
        return {"values": values, "current": mechanics.curve(values["E"], values["CPS"]), "series": series}

    def apdl(self, d: DesignInput) -> dict:
        return {"setup": apdl.build_setup_table(d, self._predict_one(d)), "script": apdl.build_script(d)}

    def validate(self, d: DesignInput, ansys: dict) -> dict:
        values = self._predict_one(d)
        rows = []
        for key, label in (("E", "Elastic modulus (MPa)"), ("CPS", "Peak stress (MPa)"), ("NU", "Poisson ratio")):
            raw = ansys.get(key)
            try:
                actual = None if raw in (None, "") else float(raw)
            except (TypeError, ValueError):
                raise DomainError(f"{key} must be a number")
            diff = verdict = None
            if actual is not None:
                diff = (actual - values[key]) / abs(values[key]) * 100
                verdict = "agrees" if abs(diff) <= 10 else "close" if abs(diff) <= 25 else "investigate"
            rows.append({"key": key, "label": label, "twin": values[key], "ansys": actual,
                         "diff_pct": None if diff is None else round(diff, 1), "verdict": verdict})
        return {"rows": rows, "ansys_rows_in_training": self.store.report["ansys_rows"], "n": self.store.report["n"]}
