# Test Strategy and Scenario Catalog

The default suite is offline and deterministic. Paid network calls are never required.

## Current automated coverage

- Typed null, empty, range, immutability and enum contracts
- Email, phone, API-key and private-key redaction
- Direct prompt-injection and clean technical-language controls
- Sliding-window rate-limit boundaries, expiry and subject isolation
- JSON/Markdown ingestion, unanswered entries, duplicates and filters
- Deterministic scoring, concept coverage and all eight dimensions
- Seeded selection, empty filters and adaptive session progression
- Happy path, pause/resume/cancel and every invalid state transition
- Retention bounds, expiry, deletion, event ordering and uniqueness
- API success, `404`, `409`, `422`, `429`-ready and `503` behavior
- Static UI contract and absence of reference-answer leakage
- WebRTC multipart contract through a mock HTTP transport
- Provider `400/401/429/500`, invalid SDP, model, voice and empty input
- Metrics output excludes answer payloads

## Manual voice checks

Browser microphone permissions, speech synthesis, interruption, device changes, background noise, long silence, overlapping speech, network handoff and accessibility require real-browser/manual or Playwright synthetic-media verification. These are documented separately rather than falsely claimed by unit tests.
