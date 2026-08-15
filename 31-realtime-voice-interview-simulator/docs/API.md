# API and State Contract

## State machine

```text
CREATED -> ACTIVE <-> PAUSED -> COMPLETED
   |          |         |
   +----------+---------+-> CANCELLED
```

Invalid transitions return HTTP `409`. Unknown identifiers return `404`; schema errors return `422`; unavailable realtime credentials/providers return `503`; admission pressure returns `429`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Readiness and voice configuration |
| GET | `/api/questions` | Safe metadata only; never reference answers |
| POST | `/api/sessions` | Create seeded, versionable interview |
| POST | `/api/sessions/{id}/start` | Present first question |
| POST | `/api/sessions/{id}/answers` | Redact, evaluate and advance |
| POST | `/api/sessions/{id}/pause` | Durable pause |
| POST | `/api/sessions/{id}/resume` | Resume without changing turn |
| POST | `/api/sessions/{id}/cancel` | Terminal cancellation |
| GET | `/api/sessions/{id}` | Session document |
| GET | `/api/sessions/{id}/summary` | Readiness report |
| GET | `/api/sessions/{id}/events` | Ordered audit journal |
| DELETE | `/api/sessions/{id}` | Subject deletion |
| POST | `/api/realtime/calls` | Authenticated SDP relay |
| GET | `/metrics` | Prometheus exposition |

The local implementation is single-user. Production must authenticate every operation and scope sessions to a tenant/subject outside candidate-controlled input.
