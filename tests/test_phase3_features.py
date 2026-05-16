from fastapi.testclient import TestClient

from api.server import app


def test_phase3_kv_put_get_metrics():
    c = TestClient(app)
    put = c.post("/phase3/kv", json={"key": "prompt-a", "token_count": 120})
    assert put.status_code == 200

    get = c.get("/phase3/kv/prompt-a")
    assert get.status_code == 200
    assert get.json()["cached_tokens"] >= 0

    m = c.get("/phase3/kv/metrics")
    assert m.status_code == 200
    assert "estimated_kv_memory_mb" in m.json()


def test_phase3_batch_submit_and_flush():
    c = TestClient(app)
    s = c.post("/phase3/batch/submit", json={"prompt": "hello batch", "quant_mode": "int8"})
    assert s.status_code == 200

    f = c.post("/phase3/batch/flush")
    assert f.status_code == 200
    body = f.json()
    assert "batch_size" in body
    assert "results" in body


def test_phase3_stream():
    c = TestClient(app)
    r = c.post("/phase3/stream", json={"text": "a b c d", "delay_sec": 0.0})
    assert r.status_code == 200
    data = r.json()
    assert data["token_count"] == 4
