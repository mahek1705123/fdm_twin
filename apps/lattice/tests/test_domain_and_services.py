"""Runs with `python manage.py test`. Service tests use the trained artifacts (run train_surrogate first)."""
from django.conf import settings
from django.test import SimpleTestCase

from apps.lattice.domain.entities import DesignInput, DomainError
from apps.lattice.domain.geometry import beams, tile
from apps.lattice.domain.mechanics import stress_at
from apps.lattice.infrastructure.dataset import DatasetRepository
from apps.lattice.infrastructure.model_store import ModelStore
from apps.lattice.services.optimisation_service import OptimisationService
from apps.lattice.services.prediction_service import PredictionService
from apps.lattice.services.twin_service import TwinService

BASE = dict(topology="Auxetic_Honeycomb", angle=-15, material="PLA", cell_size=10, wall_thickness=1,
            layer_thickness=.2, nozzle_temp=210)


class DomainTests(SimpleTestCase):
    def test_rejects_angle_not_in_dataset(self):
        with self.assertRaises(DomainError):
            DesignInput.from_dict({**BASE, "topology": "Honeycomb", "angle": 15})

    def test_rejects_out_of_range(self):
        with self.assertRaises(DomainError):
            DesignInput.from_dict({**BASE, "cell_size": 99})

    def test_every_topology_has_beams(self):
        for t, a in [("Honeycomb", 0), ("Auxetic_Honeycomb", -15), ("Chiral", 15), ("Star_Reentrant", -15)]:
            pts, segs = beams(tile(t, a))
            self.assertGreater(len(pts), 10)
            self.assertGreater(len(segs), 10)

    def test_stress_curve_is_elastic_then_bounded(self):
        self.assertAlmostEqual(stress_at(0.001, 1000, 50), 1.0)
        self.assertLessEqual(stress_at(0.3, 1000, 50), 50)


class ServiceTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.store = ModelStore(settings.LATTICE_ARTIFACT_DIR)
        cls.d = DesignInput.from_dict(BASE)

    def test_prediction_is_physical(self):
        r = PredictionService(self.store, DatasetRepository(self.store)).predict(self.d)
        self.assertLess(r["values"]["NU"], 0)  # auxetic design
        self.assertGreater(r["values"]["E"], 0)

    def test_optimiser_respects_density_limit(self):
        r = OptimisationService(self.store).search("E", 40, 0)
        self.assertTrue(all(x["values"]["RHO"] <= 40 for x in r["designs"]))

    def test_validate_flags_big_gap(self):
        r = TwinService(self.store).validate(self.d, {"E": 5000})
        self.assertEqual(r["rows"][0]["verdict"], "investigate")
