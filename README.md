# Future AI Systems (Distributed AI Infrastructure Playground)

A production-inspired AI infrastructure playground for learning and building systems across:
- Deep Learning
- Distributed Systems
- Observability
- HPC-style optimization concepts

This repository is focused on runnable infrastructure patterns, not toy model demos.

## What Is Implemented

- Inference API with trace logging and analytics
- Distributed worker-pool simulation with routing, retries, and fault injection
- KV cache simulation and continuous batching flow
- Token streaming simulation
- Quantization and memory-impact simulation
- Attention map simulation and activation analysis
- OpenTelemetry-style span export
- Streamlit observability dashboard with metrics and heatmaps
- Benchmark harness + CI performance gate
- Kubernetes deployment templates + runbook/SLO docs

## API Surface

### Core
- `GET /health`
- `POST /infer`
- `GET /traces`
- `GET /trace/{trace_id}`
- `GET /analytics`
- `GET /metrics/queue`
- `GET /metrics/rollups`

### Distributed
- `POST /distributed/infer`
- `POST /distributed/load`
- `GET /distributed/metrics`
- `GET /distributed/fault/scenarios`
- `POST /distributed/fault/scenario`

### Inference Optimization Simulation
- `GET /phase3/kv/{key}`
- `POST /phase3/kv`
- `GET /phase3/kv/metrics`
- `POST /phase3/batch/submit`
- `POST /phase3/batch/flush`
- `POST /phase3/stream`
- `GET /phase3/metrics`

### Model Internals / Observability
- `POST /transformers/attention`
- `POST /activations/extract`
- `POST /activations/drift`
- `GET /otel/spans`

## Quick Start (Local)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
./scripts/run_api.sh
```

In a second terminal:

```bash
source .venv/bin/activate
./scripts/run_dashboard.sh
```

Open:
- API docs: `http://localhost:8080/docs`
- Dashboard: `http://localhost:8501`

## Quick Start (Docker)

```bash
docker compose up --build
```

## Benchmarking

Run synthetic benchmark:

```bash
python -m benchmarks.run_benchmark --base-url http://localhost:8080 --count 300
```

CI performance gate uses:
- `benchmarks/perf_gate.py`
- thresholds configured in `.github/workflows/ci.yml`

## Repository Layout

```text
api/
core/
  tracing/
  telemetry/
  inference/
  storage/
  analytics/
  distributed/
  optimization/
  activations/
  serving/
  transformers/
dashboard/
benchmarks/
kubernetes/
docs/
tests/
```

## Documentation

- Architecture: `docs/02_architecture.md`
- Learning roadmap: `docs/03_learning_roadmap.md`
- System design: `docs/04_system_design.md`
- Runbook + SLO alerts: `docs/11_runbook_slo_alerts.md`
- Full roadmap status: `docs/10_next_phases.md`

## Project Goal

Help developers build intuition and implementation skill for real AI infrastructure behavior under load, failures, and performance constraints.
