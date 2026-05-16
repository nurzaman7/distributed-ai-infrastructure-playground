from __future__ import annotations

import os
import sys

from benchmarks.run_benchmark import run


def main() -> int:
    base_url = os.getenv("BENCH_BASE_URL", "http://127.0.0.1:8080")
    count = int(os.getenv("BENCH_COUNT", "150"))
    max_p95 = float(os.getenv("PERF_MAX_P95_MS", "350"))
    max_error_rate = float(os.getenv("PERF_MAX_ERROR_RATE", "0.05"))

    res = run(base_url=base_url, requests_count=count, prompt="perf gate request")
    error_rate = res["error_count"] / max(1, res["count"])

    print("perf_result", res)
    print("error_rate", error_rate)

    if res["p95_ms"] > max_p95:
        print(f"FAIL: p95 {res['p95_ms']} > threshold {max_p95}")
        return 1
    if error_rate > max_error_rate:
        print(f"FAIL: error_rate {error_rate:.4f} > threshold {max_error_rate}")
        return 1

    print("PASS: perf gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
