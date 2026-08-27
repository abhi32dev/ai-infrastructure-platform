# Project Memory & Developer Directives: Nexus AI Infrastructure

## 1. Project Context
- **Name**: `nexus-ai-infra`
- **Purpose**: Low-latency, high-concurrency LLM serving engine adapters, two-stage context compression RAG routing, strict JSON schema output enforcers, and concurrent benchmark sweeps.
- **Location**: `/Users/abhi/Documents/Antigravity/AI Infra & LLM`

---

## 2. Mandatory Pre-Flight Checks & Verification Standards

To guarantee robust deliveries, future developers and agents must adhere to the following directives:

1. **Verify Vector Store Memory Fallback**:
   - The test suites MUST execute successfully without any active Docker container services.
   - Any edits to `vector_store.py` must maintain the `QdrantClient(":memory:")` fallback configuration.

2. **Execute Pytest Assertions**:
   - Run the 14 project tests within the local virtual environment:
     ```bash
     .venv/bin/pytest
     ```
   - Enforce a 100% pass rate.

3. **Indentation Standards**:
   - All Python code blocks must follow clean 4-space indentations.
   - Ensure variables at the module root level start at column 1 to avoid `IndentationError` during build generation steps.

4. **Observability Fallback Integrity**:
   - Ensure the performance tracer gracefully handles headless logging modes when Langfuse is offline.
