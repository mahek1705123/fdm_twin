"""Exhaustive search of the in-range design space using the surrogate (vectorised)."""
import itertools

import numpy as np
import pandas as pd

from ..domain.constants import ANGLES, MATERIALS, TOPOLOGIES
from ..domain.entities import DomainError

GOALS = {"E": "Highest stiffness", "SPEC": "Highest specific stiffness", "SEA": "Highest energy absorption",
         "NU": "Most auxetic", "UTS": "Highest tensile strength"}


class OptimisationService:
    def __init__(self, store):
        self.store = store

    def _candidates(self) -> pd.DataFrame:
        rows = []
        for topo, mat in itertools.product(TOPOLOGIES, MATERIALS):
            layers = [0.1, 0.2, 0.3] if mat == "PLA" else [0.2]  # only PLA varies layer height in the data
            for ang, layer, L, T in itertools.product(ANGLES[topo], layers, range(5, 26), np.arange(0.5, 1.5001, 0.1)):
                rows.append({"Cell_Size_L_mm": float(L), "Wall_Thickness_T_mm": round(float(T), 1),
                             "Reentrant_Angle_deg": float(ang), "Layer_Thickness_mm": layer,
                             "Nozzle_Temp_C": float(MATERIALS[mat]["nozzle"]), "Topology_Type": topo, "Material": mat})
        return pd.DataFrame(rows)

    def search(self, goal: str, max_density: float, min_modulus: float, top: int = 6) -> dict:
        if goal not in GOALS:
            raise DomainError(f"goal must be one of {list(GOALS)}")
        frame = self._candidates()
        p = self.store.predict(frame, ["RHO", "E", "NU", "SEA", "UTS"])
        score = {"SPEC": p["E"] / p["RHO"], "NU": -p["NU"]}.get(goal, p.get(goal))
        ok = (p["RHO"] <= max_density) & (p["E"] >= min_modulus)
        idx = np.argsort(-np.where(ok, score, -np.inf))[: top]
        idx = [i for i in idx if ok[i]]
        designs = [{
            "topology": frame.at[i, "Topology_Type"], "topology_label": TOPOLOGIES[frame.at[i, "Topology_Type"]],
            "angle": frame.at[i, "Reentrant_Angle_deg"], "material": frame.at[i, "Material"],
            "material_label": MATERIALS[frame.at[i, "Material"]]["label"],
            "cell_size": frame.at[i, "Cell_Size_L_mm"], "wall_thickness": frame.at[i, "Wall_Thickness_T_mm"],
            "layer_thickness": frame.at[i, "Layer_Thickness_mm"], "nozzle_temp": frame.at[i, "Nozzle_Temp_C"],
            "values": {k: float(p[k][i]) for k in p},
        } for i in idx]
        return {"evaluated": len(frame), "feasible": int(ok.sum()), "designs": designs}
