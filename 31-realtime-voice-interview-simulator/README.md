# Project 31 — Realtime Staff/Principal Voice Interview Simulator

A runnable, repository-aware interview platform that speaks questions, accepts voice or typed answers, adapts difficulty, scores eight production-engineering dimensions, and persists redacted, auditable session artifacts.

## What is real

- Browser speech synthesis and dictation provide a no-key offline voice path.
- The interview state machine, adaptive selection, question ingestion, redaction, scoring, reports, retention and metrics are fully executable offline.
- The production voice path relays WebRTC SDP to OpenAI's Realtime API while keeping `OPENAI_API_KEY` on the server.
- Provider calls are contract-tested with HTTP mock transports; CI never needs a paid API call.

## Run in one command

```bash
make setup && make test && make run
```

Open <http://127.0.0.1:8000>. Offline speech works without credentials in a supported browser.

For realtime speech-to-speech:

```bash
export OPENAI_API_KEY="your-key"
make run
```

The key is read only by the backend and must never be placed in JavaScript or committed.

## Architecture and learning material

- [Interactive flowchart](FLOWCHART.html)
- [Standalone SVG](FLOWCHART.svg)
- [Production architecture reasoning](PROD_ARCHITECTURE_REASONING.md)
- [Staff/Principal interview question bank](INTERVIEW_PREP.md)
- [API and state contract](docs/API.md)
- [Evaluation design](docs/EVALS.md)
- [Security and privacy](docs/SECURITY.md)
- [Operations and observability](docs/OPERATIONS.md)
- [Test strategy and scenario catalog](docs/TESTING.md)
- [Complete commands](COMMANDS.md)

## Source map

| Boundary | Implementation |
|---|---|
| Typed session and evaluation contracts | `src/voice_interviewer/models.py` |
| Markdown/JSON question ingestion | `src/voice_interviewer/question_bank.py` |
| Adaptive state machine | `src/voice_interviewer/engine.py` |
| Deterministic rubric | `src/voice_interviewer/scoring.py` |
| PII, secret, injection and rate controls | `src/voice_interviewer/guardrails.py` |
| Durable state, events and retention | `src/voice_interviewer/storage.py` |
| WebRTC/OpenAI boundary | `src/voice_interviewer/realtime.py` |
| FastAPI and Prometheus surface | `src/voice_interviewer/api.py` |
| Browser voice application | `static/index.html`, `static/app.js` |

## Stored verification evidence

Run `make verify` to write `artifacts/verification.json`. The verifier checks required files, SVG/XML validity, HTML navigation, question-bank integrity, tests, secret leakage and absolute local paths.
