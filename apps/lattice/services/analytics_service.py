"""Read models for the Models tab and the Data explorer."""
from ..domain.constants import TARGETS, TOPOLOGIES


class AnalyticsService:
    def __init__(self, store):
        self.store = store

    def models_report(self) -> dict:
        r = self.store.report
        models = list(next(iter(r["metrics"].values())))
        t = {k: v for k, v in TARGETS.items()}
        return {
            "models": models, "deployed": r["deployed"], "n": r["n"], "n_test": r["n_test"], "ansys_rows": r["ansys_rows"],
            "targets": [{"key": k, "label": v[1], "unit": v[2]} for k, v in t.items()],
            "r2": {k: {m: r["metrics"][v[0]][m]["r2"] for m in models} for k, v in t.items()},
            "test": {k: r["test"][v[0]] for k, v in t.items()},
            "importance": {k: r["importance"][v[0]] for k, v in t.items()},
        }

    def dataset(self) -> dict:
        return {"rows": self.store.rows, "topologies": list(TOPOLOGIES),
                "fields": ["topology", "material", "cell_size", "wall_thickness", "angle", "layer_thickness",
                           "nozzle_temp", *TARGETS, "is_test"]}
