# Production Architecture Reasoning — Realtime Voice Interview Simulator

## 1. Objective and invariants

The system turns repository evidence into a natural spoken interview without making audio transport authoritative. Its invariants are: standard credentials never reach the browser; a candidate cannot alter policy or see private reference answers; committed turns are replay-safe; transcripts are optional and redacted; scoring is versionable; and media failure never destroys the active question.

## 2. Architecture decision record

### ADR-1: Provider-independent interview engine

**Decision:** Keep selection, state, scoring and persistence independent from voice transport.

**Why:** WebRTC, browser speech and typed input have different availability and cost but must share identical interview semantics. This also makes the core exhaustively testable offline.

**Trade-off:** More explicit state and adapter code than placing all behavior inside a realtime-model prompt.

### ADR-2: WebRTC through a server-controlled SDP relay

**Decision:** Browser sends its SDP offer to the backend; backend combines it with server-owned session configuration and authenticates `/v1/realtime/calls`.

**Why:** WebRTC is appropriate for browser media, and the standard key remains server-side.

**Trade-off:** The backend enters connection setup and needs admission, timeout and regional capacity controls.

### ADR-3: Deterministic scorer as baseline, not truth

**Decision:** Use an inspectable eight-dimensional scorer for offline learning and CI.

**Why:** Repeatable feedback is available without paid inference and judge drift.

**Trade-off:** Lexical evidence is incomplete. A calibrated semantic judge and human review are production additions.

### ADR-4: Durable event journal and bounded retention

**Decision:** Store the typed session plus ordered events in SQLite WAL locally.

**Why:** State transitions, resume and deletion are visible on one machine.

**Trade-off:** SQLite does not supply multi-region coordination, tenant authorization or distributed leases. Production uses a transactional replicated store plus event/outbox.

## 3. Conditional execution flow

1. Validate configuration and filter the versioned question bank.
2. If no question matches, reject without creating an empty session.
3. Persist `CREATED`; on start, transition to `ACTIVE` and present one question.
4. Select offline speech or realtime WebRTC. If realtime is unavailable, retain the same turn and fall back.
5. Validate/redact the finalized answer. Injection detection emits telemetry but grants no capability.
6. Score all eight dimensions and persist feedback.
7. If the question limit is reached, complete and save summary; otherwise adapt the pending order and present the next question.
8. Pause/resume preserves the current turn. Cancel and delete are distinct terminal/retention actions.

## 4. Failure-mode analysis

| Failure | Required behavior | Evidence |
|---|---|---|
| Missing API key | HTTP 503 for realtime; offline remains healthy | `RealtimeUnavailable` test |
| Provider 400/401/429/500 | Sanitized typed failure; no provider body leakage | Mock transport matrix |
| Invalid SDP/model/voice | Reject before unsafe call or response use | Contract tests |
| Empty/null/oversized answer | Schema/guardrail rejection | Boundary matrix |
| Secret/PII in transcript | Redact before scoring/persistence | Redaction tests |
| Invalid state transition | HTTP 409; no mutation | State-machine matrix |
| Process crash | Local durable session survives; production adds atomic answer idempotency | SQLite/event design |
| Media disconnect | Close tracks; retain question and text | UI disconnect path |
| Quota pressure | 429 admission; production uses distributed leases | Sliding-window tests |
| Retention expiry | Cascade-delete session artifacts | Purge tests |

## 5. Production substitutions

| Local component | Production component | Additional control |
|---|---|---|
| SQLite WAL | PostgreSQL-compatible replicated store | optimistic versions, tenant RLS, outbox |
| In-process limiter | Distributed quota service | leases, fencing, fairness, reconciliation |
| Browser speech API | Managed STT/TTS fallback | regional policy, quality eval, cost |
| Deterministic scorer | Deterministic + calibrated judge panel | version pinning, bias evaluation, human appeal |
| Local filesystem artifacts | Encrypted object store | lifecycle, residency, deletion verification |
| Single process metrics | OpenTelemetry + Prometheus | trace sampling, controlled cardinality |

## 6. Cost model

Cost is driven by concurrent audio minutes, input/output audio, transcription, semantic scoring and retention. Admission reserves a maximum session budget; live usage decrements it; close reconciles actual provider usage. Prefer short prompts, server VAD, bounded answer duration, cached static instructions and offline scoring for routine practice. Track cost per completed useful interview, not cost per API call.

## 7. What the project does not falsely claim

Mock WebRTC tests prove request/response contracts, not microphone quality, speech recognition accuracy or provider availability. Browser speech support varies. The local application is not multi-tenant authentication. Deterministic scoring is coaching evidence, not an employment decision. These boundaries are explicit in the README, tests and operations guide.
