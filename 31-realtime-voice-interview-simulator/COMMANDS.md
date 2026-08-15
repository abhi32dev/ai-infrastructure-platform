# Complete Command Reference

All commands run from `31-realtime-voice-interview-simulator/`.

```bash
# Create the isolated environment and install pinned dependencies
make setup

# Run all unit, integration, API, security and provider-contract tests
make test

# Run with statement/branch coverage
.venv/bin/python -m pytest --cov=src/voice_interviewer --cov-report=term-missing --cov-branch

# Run the deterministic CLI demonstration
make demo

# Start offline/browser-voice mode
make run

# Start real speech-to-speech mode
export OPENAI_API_KEY="your-key"
make run

# Production-style container
docker compose up --build

# Structural, SVG, security and test verification artifact
make verify
```

API smoke test:

```bash
curl -s http://127.0.0.1:8000/api/health
curl -s http://127.0.0.1:8000/api/questions
curl -s -X POST http://127.0.0.1:8000/api/sessions \
  -H 'Content-Type: application/json' \
  -d '{"mode":"incident","difficulty":"staff","question_limit":3}'
```

Never put an API key in a URL, command committed to shell history, browser storage or repository file.
