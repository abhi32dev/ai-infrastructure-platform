#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== Bootstrapping environment in: ${PROJECT_DIR} ==="

# Check python version
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed." >&2
    exit 1
fi

# Set up virtual environment
if [ ! -d "${PROJECT_DIR}/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "${PROJECT_DIR}/.venv"
fi

source "${PROJECT_DIR}/.venv/bin/activate"

echo "Installing dependency modules..."
pip install --upgrade pip
pip install -e "${PROJECT_DIR}" --upgrade

# Try to pull models in Ollama if ollama is online
if command -v ollama &> /dev/null; then
    echo "Verifying local model presence in Ollama..."
    ollama pull nomic-embed-text || true
    ollama pull qwen2.5:3b || true
    # Create candidate-brain alias if needed
    ollama show candidate-brain &>/dev/null || ollama create candidate-brain -f <(echo "FROM qwen2.5:3b") || true
else
    echo "Ollama command line not found. Skipping model preload (fallbacks will cover runtime)."
fi

echo "=== Bootstrapping Completed Successfully ==="
