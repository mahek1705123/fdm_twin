"""HTTP-level tests through Django's test client (need artifacts: run train_surrogate first)."""
import json

from django.test import SimpleTestCase

D = dict(topology="Chiral", angle=15, material="ABS", cell_size=12, wall_thickness=1, layer_thickness=.2, nozzle_temp=230)


class ApiTests(SimpleTestCase):
    def post(self, path, body):
        return self.client.post("/api/" + path, data=json.dumps(body), content_type="application/json")

    def test_meta(self):
        self.assertIn("Chiral", self.client.get("/api/meta").json()["topologies"])

    def test_predict_returns_all_targets(self):
        r = self.post("predict", {"design": D})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(set(r.json()["values"]), {"E", "UTS", "CPS", "NU", "SEA", "RHO"})

    def test_bad_design_is_400(self):
        self.assertEqual(self.post("predict", {"design": {**D, "angle": -15}}).status_code, 400)

    def test_optimise_and_apdl(self):
        self.assertEqual(self.post("optimise", {"goal": "SEA", "max_density": 50, "min_modulus": 0}).status_code, 200)
        self.assertIn("BEAM188", self.post("apdl", {"design": D}).json()["script"])

    def test_pages_render(self):
        for url in ("/", "/twin/"):
            self.assertEqual(self.client.get(url).status_code, 200)
