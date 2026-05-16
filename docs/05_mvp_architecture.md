# MVP Architecture (Phase 1)

## Scope

- Single-node but multi-component system
- Simulated inference + real observability pipeline
- Dashboard with latency/throughput/error/queue metrics

## Minimum Modules

- core/tracing
- core/telemetry
- core/inference
- core/storage
- dashboard
- api

## Exit Criteria

- API endpoints operational
- Trace persistence works under load
- Dashboard updates from live data
- Benchmark script produces reproducible numbers
