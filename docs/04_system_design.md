# System Design Blueprint

## Services

- API service: ingress and request contracts
- Worker service: inference execution and streaming
- Telemetry service: trace/event/metric ingestion
- Analytics service: aggregations and anomaly detection
- Dashboard service: visual exploration and debugging

## Storage

- JSONL for raw append-only events
- SQLite/Postgres for queryable traces and metrics
- Redis (optional) for queue/cache simulation

## Key Interfaces

- TraceRecord
- SpanRecord
- EventRecord
- ActivationRecord
- QueueMetrics
