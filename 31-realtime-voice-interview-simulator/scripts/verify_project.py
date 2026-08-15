#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "src/voice_interviewer/__init__.py", "src/voice_interviewer/api.py",
    "src/voice_interviewer/engine.py", "src/voice_interviewer/models.py",
    "src/voice_interviewer/question_bank.py", "src/voice_interviewer/scoring.py",
    "src/voice_interviewer/guardrails.py", "src/voice_interviewer/storage.py",
    "src/voice_interviewer/realtime.py", "src/voice_interviewer/observability.py",
    "tests", "static/index.html", "static/styles.css", "static/app.js",
    "README.md", "COMMANDS.md", "INTERVIEW_PREP.md", "PROD_ARCHITECTURE_REASONING.md",
    "FLOWCHART.html", "FLOWCHART.svg", "Dockerfile", "docker-compose.yml",
    "requirements.txt", "requirements-dev.txt", ".env.example",
    "docs/API.md", "docs/EVALS.md", "docs/SECURITY.md", "docs/OPERATIONS.md", "docs/TESTING.md",
)


def main() -> int:
    files = [path for path in ROOT.rglob("*") if path.is_file() and ".venv" not in path.parts and "artifacts" not in path.parts]
    text_files = [path for path in files if path.suffix.lower() in {".py", ".md", ".html", ".css", ".js", ".json", ".yml", ".yaml", ".txt", ".example"} or path.name in {"Dockerfile", "Makefile"}]
    production_files = [path for path in text_files if "tests" not in path.parts and "scripts" not in path.parts]
    corpus = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in production_files)
    browser = (ROOT / "static" / "app.js").read_text()
    checks = {
        "required_files": all((ROOT / item).exists() for item in REQUIRED),
        "unique_required_files": len(REQUIRED) == len(set(REQUIRED)),
        "svg_is_valid_xml": valid_svg(ROOT / "FLOWCHART.svg"),
        "html_links_svg": 'data="FLOWCHART.svg"' in (ROOT / "FLOWCHART.html").read_text(),
        "question_bank_has_answers": (ROOT / "INTERVIEW_PREP.md").read_text().count("**Staff/Principal answer.**") >= 10,
        "no_absolute_user_paths": "/Users/abhi" not in corpus and "file:///Users/" not in corpus,
        "no_committed_secret": not re.search(r"\bsk-[A-Za-z0-9_-]{20,}\b|BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY", corpus),
        "browser_has_no_standard_credential": "Authorization: Bearer" not in browser and not re.search(r"sk-[A-Za-z0-9_-]{20,}", browser),
        "offline_and_realtime_paths": "speechSynthesis" in corpus and "/v1/realtime/calls" in corpus,
    }
    test = subprocess.run([sys.executable, "-m", "pytest", str(ROOT / "tests"), "-q"], cwd=ROOT, text=True, capture_output=True)
    checks["tests_pass"] = test.returncode == 0
    match = re.search(r"(\d+) passed", test.stdout)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "test_count": int(match.group(1)) if match else 0,
        "test_output": test.stdout.strip(),
    }
    target = ROOT / "artifacts"; target.mkdir(exist_ok=True)
    (target / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Project 31 verification: {report['status']} ({report['test_count']} tests)")
    for name, passed in checks.items(): print(f"  {'PASS' if passed else 'FAIL'} {name}")
    if test.stderr: print(test.stderr)
    return int(report["status"] != "passed")


def valid_svg(path: Path) -> bool:
    try:
        root = ET.parse(path).getroot()
        return root.tag.endswith("svg") and root.get("viewBox") is not None
    except (ET.ParseError, OSError):
        return False


if __name__ == "__main__":
    raise SystemExit(main())
