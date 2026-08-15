import json

import httpx
import pytest
from fastapi.testclient import TestClient

from src.voice_interviewer.api import create_app
from src.voice_interviewer.realtime import RealtimeGateway, RealtimeUnavailable, interviewer_instructions


@pytest.fixture
def client(tmp_path, bank):
    app = create_app(database=tmp_path / "api.db", bank=bank, realtime=RealtimeGateway(None))
    with TestClient(app) as value: yield value


def create_started(client, limit=2):
    created = client.post("/api/sessions", json={"question_limit": limit}).json()
    return client.post(f"/api/sessions/{created['id']}/start").json()


def test_health_and_security_headers(client):
    response = client.get("/api/health")
    assert response.json() == {"status": "healthy", "questions": 3, "realtime_configured": False}
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_index_and_static_assets(client):
    assert "Principal Voice Interview Lab" in client.get("/").text
    assert "speechSynthesis" in client.get("/static/app.js").text
    assert "score-ring" in client.get("/static/styles.css").text


def test_question_list_does_not_expose_reference_answers(client):
    payload = client.get("/api/questions").json()
    assert len(payload) == 3
    assert "reference_answer" not in payload[0]
    assert len(client.get("/api/questions?tag=security").json()) == 1


def test_session_api_happy_path(client):
    session = create_started(client, 1)
    response = client.post(f"/api/sessions/{session['id']}/answers", json={"answer": "Use idempotency checkpoint deadline retry fallback metric trace security cost and scale.", "duration_seconds": 10})
    assert response.status_code == 200
    assert response.json()["state"] == "completed"
    assert client.get(f"/api/sessions/{session['id']}/summary").json()["questions_answered"] == 1
    assert len(client.get(f"/api/sessions/{session['id']}/events").json()) == 5


def test_api_validation_and_unknown_paths(client):
    assert client.post("/api/sessions", json={"question_limit": 0}).status_code == 422
    assert client.get("/api/sessions/missing").status_code == 404
    assert client.post("/api/sessions/missing/start").status_code == 404
    assert client.get("/api/sessions/missing/events").status_code == 404


def test_api_transition_conflict(client):
    created = client.post("/api/sessions", json={}).json()
    assert client.post(f"/api/sessions/{created['id']}/pause").status_code == 409


def test_api_delete(client):
    created = client.post("/api/sessions", json={}).json()
    assert client.delete(f"/api/sessions/{created['id']}").status_code == 204
    assert client.delete(f"/api/sessions/{created['id']}").status_code == 404


def test_metrics_endpoint(client):
    client.post("/api/sessions", json={})
    text = client.get("/metrics").text
    assert "voice_interviewer_sessions_total" in text
    assert "voice_interviewer_http_request_seconds_count" in text


def test_realtime_requires_started_session_and_key(client):
    created = client.post("/api/sessions", json={}).json()
    assert client.post(f"/api/realtime/calls?session_id={created['id']}", content="v=0\r\n", headers={"Content-Type": "application/sdp"}).status_code == 409
    started = client.post(f"/api/sessions/{created['id']}/start").json()
    response = client.post(f"/api/realtime/calls?session_id={started['id']}", content="v=0\r\n", headers={"Content-Type": "application/sdp"})
    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_realtime_gateway_success_and_contract():
    seen = {}
    def handler(request: httpx.Request):
        seen["authorization"] = request.headers["authorization"]
        seen["content_type"] = request.headers["content-type"]
        seen["body"] = request.content
        return httpx.Response(200, text="v=0\r\no=answer")
    gateway = RealtimeGateway("secret", client=httpx.Client(transport=httpx.MockTransport(handler)))
    answer = gateway.create_call("v=0\r\no=offer", instructions="Ask a rigorous infrastructure question.")
    assert answer.startswith("v=0")
    assert seen["authorization"] == "Bearer secret"
    assert "multipart/form-data" in seen["content_type"]
    assert b"gpt-realtime-2.1" in seen["body"]
    assert b"semantic_vad" in seen["body"]


@pytest.mark.parametrize("status", [400, 401, 429, 500])
def test_realtime_gateway_sanitizes_provider_errors(status):
    transport = httpx.MockTransport(lambda request: httpx.Response(status, text="secret provider detail", headers={"x-request-id": "req-safe"}))
    gateway = RealtimeGateway("secret", client=httpx.Client(transport=transport))
    with pytest.raises(RealtimeUnavailable) as exc: gateway.create_call("v=0\r\n", instructions="valid instructions here")
    assert "req-safe" in str(exc.value)
    assert "secret provider detail" not in str(exc.value)


def test_realtime_gateway_rejects_invalid_response_model_voice_and_empty_input():
    gateway = RealtimeGateway("secret", client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, text="json"))))
    with pytest.raises(RealtimeUnavailable, match="invalid SDP"): gateway.create_call("v=0\r\n", instructions="valid instructions here")
    with pytest.raises(ValueError, match="model"): gateway.create_call("v=0", instructions="valid instructions here", model="text-model")
    with pytest.raises(ValueError, match="voice"): gateway.create_call("v=0", instructions="valid instructions here", voice="unknown")
    with pytest.raises(ValueError): gateway.create_call("", instructions="valid instructions here")


def test_interviewer_instructions_are_bounded_and_fail_closed():
    value = interviewer_instructions("How does it work?", "reference " * 2000, "principal")
    assert "principal" in value
    assert "How does it work?" in value
    assert "never recite" in value
    assert len(value) < 7000
