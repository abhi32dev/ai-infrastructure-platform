from pathlib import Path
from tempfile import TemporaryDirectory

from src.voice_interviewer.engine import InterviewEngine
from src.voice_interviewer.models import InterviewConfig
from src.voice_interviewer.question_bank import QuestionBank
from src.voice_interviewer.storage import SQLiteSessionStore


if __name__ == "__main__":
    project = Path(__file__).resolve().parent
    repository = project.parent
    bank = QuestionBank.from_repository(repository, project / "data" / "questions.json")
    with TemporaryDirectory() as directory:
        store = SQLiteSessionStore(Path(directory) / "demo.db")
        engine = InterviewEngine(bank, store)
        session = engine.create(InterviewConfig(projects=("31-realtime",), question_limit=2))
        session = engine.start(session.id)
        print(f"Question: {session.turns[-1].question.prompt}")
        required = ", ".join(session.turns[-1].question.required_concepts)
        answer = (
            f"The invariant is safe progress and bounded behavior. The mechanism covers {required}. "
            "First define the service and data-plane boundary; second explain the trade-off between latency, cost, and complexity. "
            "For failure, use an end-to-end timeout, retry, fallback, rollback, reconciliation and backpressure. "
            "Authorize every tenant with least privilege and audit the decision. Measure p95 and p99 latency, trace the operation, "
            "alert on SLO burn, and capacity-plan partitions, shards, throughput and GPU use. Finally cite the concrete implementation."
        )
        session = engine.submit_answer(session.id, answer, duration_seconds=34)
        evaluation = session.turns[0].evaluation
        print(f"Score: {evaluation.total_score}/100 ({evaluation.level})")
        print(f"Next: {session.turns[-1].question.prompt}")
        store.close()
