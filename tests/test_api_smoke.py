from fastapi.testclient import TestClient
from api.server import app


def test_health():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_infer_and_traces():
    c = TestClient(app)
    r = c.post("/infer", json={"prompt": "hello world"})
    assert r.status_code == 200
    body = r.json()
    assert "trace_id" in body

    t = c.get("/traces?limit=20")
    assert t.status_code == 200
    assert isinstance(t.json(), list)
