"""Composition root: the only place that wires infrastructure into services."""
from functools import lru_cache
from types import SimpleNamespace

from django.conf import settings

from ..infrastructure.dataset import DatasetRepository
from ..infrastructure.model_store import ModelStore
from .analytics_service import AnalyticsService
from .optimisation_service import OptimisationService
from .prediction_service import PredictionService
from .twin_service import TwinService


@lru_cache(maxsize=1)
def get_services():
    store = ModelStore(settings.LATTICE_ARTIFACT_DIR)
    dataset = DatasetRepository(store)
    return SimpleNamespace(prediction=PredictionService(store, dataset), optimisation=OptimisationService(store),
                           twin=TwinService(store), analytics=AnalyticsService(store))
