"""Loads the trained pipelines from disk and exposes batch prediction on DataFrames."""
import json
from pathlib import Path

import joblib
import pandas as pd

from ..domain.constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGETS


class ArtifactsMissing(RuntimeError):
    pass


class ModelStore:
    def __init__(self, artifact_dir: Path):
        self.dir = Path(artifact_dir)
        self._models = None
        self._report = None
        self._rows = None

    def _require(self, name):
        p = self.dir / name
        if not p.exists():
            raise ArtifactsMissing(f"{p} not found. Run: python manage.py train_surrogate")
        return p

    @property
    def models(self):
        if self._models is None:
            self._models = joblib.load(self._require("models.joblib"))
        return self._models

    @property
    def report(self) -> dict:
        if self._report is None:
            self._report = json.loads(self._require("report.json").read_text())
        return self._report

    @property
    def rows(self) -> list:
        if self._rows is None:
            self._rows = json.loads(self._require("rows.json").read_text())
        return self._rows

    def predict(self, frame: pd.DataFrame, keys=None) -> dict:
        frame = frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        out = {}
        for k in keys or TARGETS:
            v = self.models[k].predict(frame)
            if k in ("E", "RHO"):
                v = v.clip(min=1.0)
            out[k] = v
        return out
