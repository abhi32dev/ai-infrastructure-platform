from __future__ import annotations

import threading
import time
from collections import Counter, defaultdict
from contextlib import contextmanager
from typing import Iterator


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: Counter[tuple[str, tuple[tuple[str, str], ...]]] = Counter()
        self._durations: dict[str, list[float]] = defaultdict(list)

    def increment(self, name: str, value: int = 1, **labels: str) -> None:
        if value < 0:
            raise ValueError("counter increments cannot be negative")
        key = (name, tuple(sorted((item, str(label)) for item, label in labels.items())))
        with self._lock:
            self._counters[key] += value

    @contextmanager
    def latency(self, name: str) -> Iterator[None]:
        started = time.perf_counter()
        try:
            yield
        finally:
            with self._lock:
                self._durations[name].append(time.perf_counter() - started)

    def snapshot(self) -> dict:
        with self._lock:
            counters = {
                f"{name}{_label_text(labels)}": value
                for (name, labels), value in self._counters.items()
            }
            durations = {
                name: {"count": len(values), "average_seconds": sum(values) / len(values), "max_seconds": max(values)}
                for name, values in self._durations.items() if values
            }
        return {"counters": counters, "durations": durations}

    def prometheus(self) -> str:
        lines: list[str] = []
        with self._lock:
            for (name, labels), value in sorted(self._counters.items()):
                lines.append(f"voice_interviewer_{name}{_label_text(labels)} {value}")
            for name, values in sorted(self._durations.items()):
                if values:
                    lines.append(f"voice_interviewer_{name}_seconds_count {len(values)}")
                    lines.append(f"voice_interviewer_{name}_seconds_sum {sum(values):.9f}")
        return "\n".join(lines) + "\n"


def _label_text(labels: tuple[tuple[str, str], ...]) -> str:
    if not labels:
        return ""
    return "{" + ",".join(f'{key}="{value}"' for key, value in labels) + "}"
