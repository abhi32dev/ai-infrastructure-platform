# Project 31 Staff/Principal Interview Question Bank

## Q1: Why does the application support both direct speech-to-speech and an offline/chained path?

**Staff/Principal answer.** Direct speech-to-speech provides the lowest perceived latency, native interruption and natural turn-taking. It also couples availability and variable cost to a realtime provider. The offline path keeps the interview state machine, browser speech synthesis/dictation, deterministic scoring and artifacts usable without credentials. A chained STT → text policy → TTS design gives tighter control over intermediate text but adds latency and more failure boundaries. The platform owns one `InterviewEngine`; transport is replaceable.

**Code evidence.** `static/app.js` implements `speak`, `dictate` and `realtime`. `src/voice_interviewer/realtime.py · RealtimeGateway.create_call` owns the provider boundary.

## Q2: Where are the trust and credential boundaries?

**Staff/Principal answer.** Browser SDP, audio and transcript are untrusted. The backend authenticates/admit-limits the caller, builds server-owned instructions and relays SDP using the standard API key. The key never reaches JavaScript. Reference answers remain server-side and are omitted from the question-list API. In production, every session lookup also requires tenant/subject authorization; an unguessable ID alone is not authorization.

```python
# src/voice_interviewer/realtime.py
response = self.client.post(
    self.endpoint,
    headers={"Authorization": f"Bearer {self.api_key}"},
    files={"sdp": (None, offer, "application/sdp"),
           "session": (None, json.dumps(session), "application/json")},
)
```

## Q3: Where is the answer-submission linearization point?

**Staff/Principal answer.** It is the authoritative transaction that commits the redacted answer, evaluation, turn version and event/outbox identity—not speech completion. The local lab serializes the session document and append-only events in SQLite, but the session save and event are separate commits, so it accurately documents that production needs a single transaction, idempotency key and optimistic version. A retry after a committed-but-unacknowledged response must return the prior evaluation instead of scoring twice.

**Code evidence.** `InterviewEngine.submit_answer` owns the mutation; `SQLiteSessionStore.save` and `append_event` expose the local transaction boundaries.

## Q4: How does adaptive questioning remain reproducible and fair?

**Staff/Principal answer.** Pin a versioned question bank, use a deterministic seed, persist the candidate set and selection reason, separate selection from scoring, and retain common anchor questions. Never adapt based on protected attributes. Compare path coverage and outcomes across relevant slices, report uncertainty when paths diverge, and provide a nonadaptive mode for standardized assessment. The lab shuffles with `config.seed` and adaptation is explicitly switchable.

```python
random.Random(config.seed).shuffle(candidates)
if not session.config.adaptive or not session.pending_question_ids:
    return
```

## Q5: Why is the deterministic scorer intentionally limited?

**Staff/Principal answer.** It makes required-concept and production-dimension behavior inspectable, repeatable and safe for CI; it does not claim semantic equivalence to an expert. Keyword coverage can be gamed and cannot establish factual correctness. A production design adds a calibrated semantic judge and expert review, but deterministic controls still enforce forbidden claims, code-reference resolution and hard safety policy. Store model, prompt, rubric and dataset versions and measure judge disagreement.

**Code evidence.** `DeterministicScorer.evaluate` returns all eight bounded dimensions and an explicit improved-answer scaffold.

## Q6: How should failures degrade without losing interview progress?

**Staff/Principal answer.** Audio transport never owns business state. Persist the active turn before media negotiation. On WebRTC/provider failure, close tracks, preserve the unanswered turn and offer browser dictation or typed input. Use one end-to-end deadline; do not retry media indefinitely. Partial transcript is marked incomplete. Provider usage and quota reservations are reconciled after ambiguous disconnects. The UI `disconnectVoice` leaves `session` and `answer` intact.

## Q7: Which information is safe to observe?

**Staff/Principal answer.** Observe correlation IDs, state transition, model/voice version, negotiation latency, time to first audio, VAD/interrupt signals, transcript-finalization status, scoring duration, redaction category, usage and cost. Do not emit raw audio, reference answers, full transcript, secrets or chain-of-thought. Cardinality must be bounded: project/tag labels need controlled vocabularies, while session IDs belong in traces/logs rather than metric labels.

**Code evidence.** `Metrics.prometheus` emits counters and latency aggregates only; tests assert answer content is absent.

## Q8: How do retention and deletion work?

**Staff/Principal answer.** Transcript retention is independent of audio consent. The default records no raw audio. Answers are redacted before persistence; retention is bounded; deletion cascades through events and summaries locally. Production must also delete derived reports, caches, object storage and backups according to policy, while recording a content-free deletion audit. Legal holds need a distinct authorized workflow, not silent retention.

```python
# src/voice_interviewer/storage.py
cursor = self.connection.execute("DELETE FROM sessions WHERE id=?", (session_id,))
# events/summaries use ON DELETE CASCADE
```

## Q9: What changes at ten thousand concurrent global sessions?

**Staff/Principal answer.** Use regional media edges and keep the application control plane stateless. Replace SQLite with a partitioned transactional store, append events to a durable log, place artifacts in object storage and use a consistent quota/lease service. Add tenant fairness, admission, load shedding, backpressure, residency, failover and asynchronous scoring/report generation. Scale on concurrent audio minutes and negotiation rate, not HTTP request count alone.

## Q10: How is this tested without pretending that mocks prove audio quality?

**Staff/Principal answer.** Separate deterministic logic from media adapters. Unit-test schemas, selection, scoring, guardrails and retention; integration-test the API and SQLite; contract-test multipart WebRTC relay with mock transports; use synthetic audio and browser automation for media events; run chaos disconnects and a small opt-in live canary. CI never requires a key. Human listening and noisy-device tests are reported separately because mock SDP does not prove speech quality.

**Code evidence.** `tests/test_api_realtime.py` covers SDP/provider contracts; `docs/TESTING.md` explicitly lists manual media checks.
