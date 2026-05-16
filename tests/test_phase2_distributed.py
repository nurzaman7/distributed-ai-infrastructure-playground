from fastapi.testclient import TestClient

from api.server import app


def test_distributed_infer_endpoint():
    c = TestClient(app)
    r = c.post("/distributed/infer", json={"prompt": "debug batch queue", "retries": 1})
    assert r.status_code == 200
    body = r.json()
    assert "routing" in body
    assert "distributed" in body


def test_distributed_metrics_endpoint():
    c = TestClient(app)
    r = c.get("/distributed/metrics")
    assert r.status_code == 200
    body = r.json()
    assert "worker_pool" in body
    assert "queue" in body
    assert "router" in body
