from fastapi.testclient import TestClient

from api.server import app


def test_attention_endpoint():
    c = TestClient(app)
    r = c.post("/transformers/attention", json={"text": "the quick brown fox"})
    assert r.status_code == 200
    data = r.json()
    assert "attention_matrix" in data
    assert len(data["tokens"]) == 4


def test_activations_extract_and_drift():
    c = TestClient(app)
    r = c.post("/activations/extract", json={"num_layers": 3, "hidden_dim": 16, "seed": 1})
    assert r.status_code == 200
    layers = r.json()
    assert "layer_0" in layers

    v1 = layers["layer_0"]["vector"]
    v2 = layers["layer_1"]["vector"]
    d = c.post("/activations/drift", json={"v1": v1, "v2": v2})
    assert d.status_code == 200
    assert "drift_score" in d.json()


def test_fault_scenario_switch():
    c = TestClient(app)
    s = c.get("/distributed/fault/scenarios")
    assert s.status_code == 200
    assert "stable" in s.json()["scenarios"]

    setr = c.post("/distributed/fault/scenario", json={"name": "degraded"})
    assert setr.status_code == 200
    body = setr.json()
    assert body["active_scenario"] == "degraded"
