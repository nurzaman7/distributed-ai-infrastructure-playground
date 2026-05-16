from fastapi.testclient import TestClient

from api.server import app


def test_otel_spans_endpoint_shape():
    c = TestClient(app)
    c.post("/infer", json={"prompt": "otel shape test"})
    r = c.get("/otel/spans?limit=10")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        assert "trace_id" in data[0]
        assert "attributes" in data[0]
