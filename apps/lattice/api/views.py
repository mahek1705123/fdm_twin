"""HTTP/JSON adapters. No business logic here: parse -> call a service -> return JSON."""
import json
from functools import wraps

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ..domain.constants import ANGLES, MATERIALS, RANGES, TARGETS, TOPOLOGIES
from ..domain.entities import DesignInput, DomainError
from ..infrastructure.model_store import ArtifactsMissing
from ..services.container import get_services
from ..services.optimisation_service import GOALS


def endpoint(method):
    def deco(fn):
        @wraps(fn)
        @require_http_methods([method])
        def wrapper(request, *a, **kw):
            try:
                body = json.loads(request.body or b"{}") if method == "POST" else {}
                return JsonResponse(fn(request, body, get_services(), *a, **kw))
            except (DomainError, json.JSONDecodeError) as exc:
                return JsonResponse({"error": str(exc)}, status=400)
            except ArtifactsMissing as exc:
                return JsonResponse({"error": str(exc)}, status=503)
        return wrapper
    return deco


def _design(body):
    return DesignInput.from_dict(body.get("design", {}))


@endpoint("GET")
def meta(request, body, svc):
    return {
        "topologies": TOPOLOGIES, "angles": ANGLES, "ranges": RANGES, "goals": GOALS,
        "materials": {k: {"label": v["label"], "nozzle": v["nozzle"], "fibre_wt": v["fibre_wt"]} for k, v in MATERIALS.items()},
        "targets": {k: {"label": v[1], "unit": v[2]} for k, v in TARGETS.items()},
    }


@endpoint("POST")
def predict(request, body, svc):
    return svc.prediction.predict(_design(body))


@endpoint("POST")
def compare(request, body, svc):
    return {"items": svc.prediction.compare_topologies(_design(body), body.get("metric", "E"))}


@endpoint("POST")
def sensitivity(request, body, svc):
    return svc.prediction.sensitivity(_design(body), body.get("variable", "cell_size"), body.get("metric", "E"))


@endpoint("POST")
def optimise(request, body, svc):
    try:
        return svc.optimisation.search(body.get("goal", "E"), float(body.get("max_density", 60)), float(body.get("min_modulus", 0)))
    except (TypeError, ValueError) as exc:
        raise DomainError(str(exc)) from exc


@endpoint("GET")
def models(request, body, svc):
    return svc.analytics.models_report()


@endpoint("GET")
def dataset(request, body, svc):
    return svc.analytics.dataset()


@endpoint("POST")
def geometry(request, body, svc):
    return svc.twin.geometry(_design(body))


@endpoint("POST")
def curves(request, body, svc):
    return svc.twin.curves(_design(body))


@endpoint("POST")
def apdl(request, body, svc):
    return svc.twin.apdl(_design(body))


@endpoint("POST")
def validate(request, body, svc):
    return svc.twin.validate(_design(body), body.get("ansys", {}))
