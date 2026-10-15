# FDM Lattice Surrogate Lab + ANSYS Digital Twin (Django)

Two dashboards on one Django project:
* `/` ML surrogate: predict, optimise, compare 8 models, explore the dataset
* `/twin/` ANSYS digital twin: virtual compression test, stress-strain, APDL export, FEA cross-check

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py train_surrogate     # ~10 s, rebuilds artifacts/ for YOUR scikit-learn version
python manage.py runserver           # open http://127.0.0.1:8000/
python manage.py test                # domain, service and API tests
```
`artifacts/` ships pre-trained with scikit-learn 1.8. If you see a version warning or unpickling error, run `train_surrogate`.
To use new data, replace `data/fdm_lattice_ml_dataset_clean.csv` (same columns) and retrain.

## Layers (dependencies point downwards only)
```
web/ + api/          presentation   templates, static JS, JSON views. No business logic.
services/            application    PredictionService, OptimisationService, TwinService, AnalyticsService
                                    container.py is the composition root (wires everything)
infrastructure/      adapters       training.py (sklearn), model_store.py (joblib), dataset.py, apdl.py
domain/              core           constants, DesignInput validation, lattice geometry, stress-strain maths
                                    pure Python: no Django, pandas or sklearn imports
```
Rules: views call services; services use the store and domain; domain imports nothing from the other layers.
To swap the model (e.g. XGBoost), change `DEPLOYED_MODEL` and `_estimators()` in `infrastructure/training.py`. Nothing else changes.

## JSON API
| Method | Path | Purpose |
|---|---|---|
| GET | `/api/meta` | topologies, angles, materials, input ranges, targets |
| POST | `/api/predict` | `{design}` -> six predictions, nearest dataset row, confidence |
| POST | `/api/compare` | `{design, metric}` -> same settings across four topologies |
| POST | `/api/sensitivity` | `{design, variable, metric}` -> sweep one input |
| POST | `/api/optimise` | `{goal, max_density, min_modulus}` -> top designs from ~8,300 candidates |
| GET | `/api/models`, `/api/dataset` | test metrics, actual-vs-predicted, importances; dataset rows |
| POST | `/api/geometry`, `/api/curves`, `/api/apdl`, `/api/validate` | digital-twin endpoints |

`design` = `{topology, angle, material, cell_size, wall_thickness, layer_thickness, nozzle_temp}`. Invalid input returns HTTP 400 with `{"error": ...}`.

## Honest limits
* Poisson ratio, SEA and density are near-deterministic in the data (your notebook notes ~90% of rows come from a physics scaling model), so their high R² is expected. Compressive peak stress is the weak target (R² ~0.6).
* Stress-strain curves and lattice drawings are idealised from the surrogate, not FEA output.
* The APDL script is a starting template with typical bulk material values: use your coupon data and validate the model.
* Not modelled: build angle, loading direction, annealing (no variance in the dataset).
