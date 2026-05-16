# Runbook, SLOs, and Alert Patterns

## Core SLOs

- API availability: 99.9% (`/health` success)
- p95 latency (infer): < 600ms baseline simulation
- error rate: < 10% during benchmark mode
- queue drop rate: < 2% over rolling 5 minutes

## Alerts

- `HighP95Latency`: p95 > 600ms for 10 minutes
- `HighErrorRate`: error rate > 10% for 5 minutes
- `QueueBackpressure`: queue depth > 75% capacity for 5 minutes
- `QueueDrops`: dropped_total increases continuously for 3 minutes

## Triage Steps

1. Check `GET /metrics/queue` and `GET /distributed/metrics`.
2. Run synthetic load for controlled reproduction.
3. Compare `/analytics` with `/metrics/rollups` trends.
4. Reduce failure rates and tune retries for recovery.

## Recovery Levers

- lower failure injection rates for stabilization
- adjust retries/backoff in distributed calls
- decrease batch size to reduce tail latency
- scale API replicas (kubernetes deployment)
