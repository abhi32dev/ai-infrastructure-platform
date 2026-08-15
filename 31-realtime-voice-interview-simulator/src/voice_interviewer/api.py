from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .engine import InterviewEngine, InvalidTransition
from .guardrails import SlidingWindowRateLimiter
from .models import InterviewConfig
from .observability import Metrics
from .question_bank import QuestionBank
from .realtime import RealtimeGateway, RealtimeUnavailable, interviewer_instructions
from .scoring import DeterministicScorer
from .storage import SQLiteSessionStore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = PROJECT_ROOT.parent


class AnswerRequest(BaseModel):
    answer: str
    duration_seconds: float = Field(default=0.0, ge=0.0, le=10_800.0)


def create_app(*, database: Path | None = None, bank: QuestionBank | None = None, realtime: RealtimeGateway | None = None) -> FastAPI:
    metrics = Metrics()
    question_bank = bank or QuestionBank.from_repository(REPOSITORY_ROOT, PROJECT_ROOT / "data" / "questions.json")
    store = SQLiteSessionStore(database or Path(os.getenv("INTERVIEW_DB", PROJECT_ROOT / "data" / "interviews.db")))
    engine = InterviewEngine(question_bank, store, DeterministicScorer(), metrics)
    gateway = realtime or RealtimeGateway(os.getenv("OPENAI_API_KEY"))
    limiter = SlidingWindowRateLimiter(limit=int(os.getenv("INTERVIEW_RATE_LIMIT", "60")), window_seconds=60)

    app = FastAPI(title="Staff/Principal Realtime Voice Interview Simulator", version="1.0.0")
    app.state.engine = engine
    app.state.store = store
    app.state.realtime = gateway

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        subject = request.client.host if request.client else "local"
        if request.url.path.startswith("/api/") and not limiter.allow(subject):
            return Response(status_code=429, content="rate limit exceeded")
        with metrics.latency("http_request"):
            response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "healthy", "questions": len(question_bank.questions), "realtime_configured": bool(gateway.api_key)}

    @app.get("/api/questions")
    def questions(project: str | None = None, tag: str | None = None) -> list[dict]:
        selected = question_bank.filter(projects=(project.lower(),) if project else (), tags=(tag.lower(),) if tag else ())
        return [{"id": q.id, "project": q.project, "prompt": q.prompt, "tags": q.tags, "difficulty": q.difficulty} for q in selected]

    @app.post("/api/sessions", status_code=201)
    def create_session(config: InterviewConfig) -> dict:
        return engine.create(config).model_dump(mode="json")

    @app.post("/api/sessions/{session_id}/start")
    def start_session(session_id: str) -> dict:
        return _run(lambda: engine.start(session_id))

    @app.post("/api/sessions/{session_id}/answers")
    def answer(session_id: str, payload: AnswerRequest) -> dict:
        return _run(lambda: engine.submit_answer(session_id, payload.answer, payload.duration_seconds))

    @app.post("/api/sessions/{session_id}/pause")
    def pause(session_id: str) -> dict:
        return _run(lambda: engine.pause(session_id))

    @app.post("/api/sessions/{session_id}/resume")
    def resume(session_id: str) -> dict:
        return _run(lambda: engine.resume(session_id))

    @app.post("/api/sessions/{session_id}/cancel")
    def cancel(session_id: str) -> dict:
        return _run(lambda: engine.cancel(session_id))

    @app.get("/api/sessions/{session_id}")
    def get_session(session_id: str) -> dict:
        return _run(lambda: store.get(session_id))

    @app.get("/api/sessions/{session_id}/summary")
    def summary(session_id: str) -> dict:
        return _run(lambda: engine.summary(session_id))

    @app.get("/api/sessions/{session_id}/events")
    def events(session_id: str) -> list[dict]:
        try:
            store.get(session_id)
            return [event.model_dump(mode="json") for event in store.events(session_id)]
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.delete("/api/sessions/{session_id}", status_code=204)
    def delete_session(session_id: str) -> Response:
        if not store.delete(session_id):
            raise HTTPException(status_code=404, detail="unknown session")
        return Response(status_code=204)

    @app.post("/api/realtime/calls", response_class=PlainTextResponse)
    async def realtime_call(request: Request, session_id: str = Query(min_length=5), voice: str = Query(default="marin")) -> str:
        try:
            session = store.get(session_id)
            if not session.turns:
                raise InvalidTransition("start the interview before opening voice")
            question = session.turns[-1].question
            sdp = (await request.body()).decode("utf-8")
            instructions = interviewer_instructions(question.prompt, question.reference_answer, session.config.difficulty.value)
            with metrics.latency("realtime_connection"):
                return gateway.create_call(sdp, instructions=instructions, voice=voice)
        except RealtimeUnavailable as exc:
            metrics.increment("realtime_failures_total")
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except InvalidTransition as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/metrics", response_class=PlainTextResponse)
    def prometheus_metrics() -> str:
        return metrics.prometheus()

    static = PROJECT_ROOT / "static"
    app.mount("/static", StaticFiles(directory=static), name="static")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(static / "index.html")

    return app


def _run(operation):
    try:
        value = operation()
        return value.model_dump(mode="json")
    except ValueError as exc:
        message = str(exc)
        status = 404 if message.startswith("unknown") else 422
        raise HTTPException(status_code=status, detail=message) from exc
    except InvalidTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
