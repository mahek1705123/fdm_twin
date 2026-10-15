"""Offline training: compares 8 models per target, saves the deployed one plus a JSON report."""
import json
import sys

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, PolynomialFeatures, StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

from ..domain.constants import (CATEGORICAL_FEATURES, DEPLOYED_MODEL, MATERIALS, NUMERIC_FEATURES, TARGETS,
                                TOPOLOGIES)

RS = 42
TOPO, MAT = list(TOPOLOGIES), list(MATERIALS)
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_lattice_frame(csv_path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    return df[df.Topology_Type.isin(TOPO) & df.Material.isin(MAT)].reset_index(drop=True)


def _estimators():
    return {
        "Linear": LinearRegression(), "Ridge": Ridge(1.0),
        "Polynomial(2)": make_pipeline(PolynomialFeatures(2, include_bias=False), Ridge(1.0)),
        "DecisionTree": DecisionTreeRegressor(max_depth=8, random_state=RS),
        "RandomForest": RandomForestRegressor(300, random_state=RS, n_jobs=-1),
        "GradientBoosting": GradientBoostingRegressor(random_state=RS),
        "SVR(RBF)": SVR(C=10, epsilon=0.05),
        "MLP": MLPRegressor(hidden_layer_sizes=(32, 16), activation="tanh", alpha=1e-3, max_iter=6000, random_state=RS),
    }


def _pipeline(estimator, log: bool):
    pre = ColumnTransformer([
        ("num", "passthrough", NUMERIC_FEATURES),
        ("cat", OneHotEncoder(categories=[TOPO, MAT], sparse_output=False), CATEGORICAL_FEATURES),
    ])
    base = Pipeline([("pre", pre), ("scale", StandardScaler()), ("model", estimator)])
    y_tf = (Pipeline([("log", FunctionTransformer(np.log1p, np.expm1)), ("sc", StandardScaler())])
            if log else StandardScaler())
    return TransformedTargetRegressor(regressor=base, transformer=y_tf)


def _group_importance(model, X_te, y_te, base_r2, rng, repeats=15):
    groups = {"Cell size L": ["Cell_Size_L_mm"], "Wall thickness T": ["Wall_Thickness_T_mm"],
              "Re-entrant angle": ["Reentrant_Angle_deg"], "Layer thickness": ["Layer_Thickness_mm"],
              "Nozzle temp": ["Nozzle_Temp_C"], "Topology": ["Topology_Type"], "Material": ["Material"]}
    out = {}
    for name, cols in groups.items():
        drops = []
        for _ in range(repeats):
            Xp = X_te.copy()
            Xp[cols] = Xp[cols].values[rng.permutation(len(Xp))]
            drops.append(base_r2 - r2_score(y_te, model.predict(Xp)))
        out[name] = round(float(max(np.mean(drops), 0)), 4)
    return out


def train_and_save(csv_path, out_dir, log=print):
    d = load_lattice_frame(csv_path)
    X = d[FEATURES]
    tr, te = train_test_split(np.arange(len(d)), test_size=0.2, random_state=RS, stratify=d.Topology_Type)
    rng = np.random.default_rng(RS)
    deployed, metrics, test_pts, importance = {}, {}, {}, {}

    for key, (col, _label, _unit, is_log) in TARGETS.items():
        y = d[col]
        metrics[col] = {}
        for name, est in _estimators().items():
            model = _pipeline(est, is_log).fit(X.iloc[tr], y.iloc[tr])
            pred = model.predict(X.iloc[te])
            metrics[col][name] = {
                "r2": round(float(r2_score(y.iloc[te], pred)), 4),
                "mae": round(float(mean_absolute_error(y.iloc[te], pred)), 3),
                "train_r2": round(float(r2_score(y.iloc[tr], model.predict(X.iloc[tr]))), 4),
            }
            if name == DEPLOYED_MODEL:
                deployed[key] = model
                test_pts[col] = [[round(float(a), 3), round(float(b), 3)] for a, b in zip(y.iloc[te], pred)]
                importance[col] = _group_importance(model, X.iloc[te], y.iloc[te], metrics[col][name]["r2"], rng)
        log(f"{key:4s} " + "  ".join(f"{n}={m['r2']:.3f}" for n, m in metrics[col].items()))

    test_set = set(te.tolist())
    rows = [[TOPO.index(r.Topology_Type), MAT.index(r.Material), r.Cell_Size_L_mm, r.Wall_Thickness_T_mm,
             r.Reentrant_Angle_deg, r.Layer_Thickness_mm, r.Nozzle_Temp_C]
            + [round(float(getattr(r, TARGETS[k][0])), 3) for k in TARGETS] + [int(i in test_set)]
            for i, r in enumerate(d.itertuples())]
    report = {"metrics": metrics, "test": test_pts, "importance": importance, "n": len(d), "n_test": len(te),
              "ansys_rows": int((d.Data_Source_Type == "ANSYS_FEA_Validated").sum()),
              "deployed": DEPLOYED_MODEL, "sklearn": sklearn.__version__, "python": sys.version.split()[0]}
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(deployed, out_dir / "models.joblib", compress=3)
    (out_dir / "report.json").write_text(json.dumps(report, separators=(",", ":")))
    (out_dir / "rows.json").write_text(json.dumps(rows, separators=(",", ":")))
    return report
