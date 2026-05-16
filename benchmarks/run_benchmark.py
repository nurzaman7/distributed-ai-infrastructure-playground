from __future__ import annotations

import argparse
import statistics
import time

import httpx


def run(base_url: str, requests_count: int, prompt: str) -> dict:
    latencies = []
    errors = 0
    started = time.perf_counter()

    with httpx.Client(timeout=10.0) as client:
        for _ in range(requests_count):
            t0 = time.perf_counter()
            resp = client.post(f"{base_url.rstrip('/')}/infer", json={"prompt": prompt})
            latencies.append((time.perf_counter() - t0) * 1000)
            if resp.status_code != 200:
                errors += 1

    elapsed = time.perf_counter() - started
    p50 = statistics.quantiles(latencies, n=100)[49] if len(latencies) >= 100 else statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=100)[94] if len(latencies) >= 100 else max(latencies)
    p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)

    return {
        "count": requests_count,
        "elapsed_sec": round(elapsed, 3),
        "throughput_rps": round(requests_count / max(elapsed, 0.001), 3),
        "p50_ms": round(p50, 3),
        "p95_ms": round(p95, 3),
        "p99_ms": round(p99, 3),
        "error_count": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8080")
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--prompt", default="benchmark request")
    args = parser.parse_args()

    result = run(args.base_url, args.count, args.prompt)
    print(result)


if __name__ == "__main__":
    main()
