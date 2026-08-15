.PHONY: setup test run demo verify

setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements-dev.txt

test:
	.venv/bin/python -m pytest -q

run:
	.venv/bin/uvicorn app:app --reload --host 127.0.0.1 --port 8000

demo:
	.venv/bin/python demo_runner.py

verify:
	.venv/bin/python scripts/verify_project.py
