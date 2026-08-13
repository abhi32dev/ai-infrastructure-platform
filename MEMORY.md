# Master Memory & AI Infrastructure Operating System Directives

## 1. Candidate & Project Context
- **Candidate Profile**: Abhishek Singh — Staff / Principal AI Platform & Agent Infrastructure Architect (12+ years distributed systems/Python, Comcast CONDOR founding architect for 12,000+ edge nodes across 108M users, 2.4M events/day, 99.999% SLA).
- **GitHub Account**: `abhi32dev`
- **GitHub Repository**: `https://github.com/abhi32dev/ai-infrastructure-platform`
- **Live Showcase URL**: `https://abhi32dev.github.io/ai-infrastructure-platform/`
- **Workspace Location**: `/Users/abhi/Documents/Antigravity`

---

## 2. Mandatory Pre-Flight Verification Checklist
Before completing any user request or delivering final output, ALWAYS perform the following pre-flight checks:

1. **Verify All Project Links in `index.html`**:
   - Ensure every project tile/card is fully clickable and links to valid GitHub repository tree URLs (`https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/<project_dir>`).
   - Ensure all `Blueprint →` links correctly resolve to `https://github.com/abhi32dev/ai-infrastructure-platform/blob/main/<project_dir>/PROD_ARCHITECTURE_REASONING.md`.
   - Test that clicking anywhere on the tile card cleanly opens the project directory.

2. **Execute Full Test Suite Verification**:
   - Run `python3 tests/run_all_20_project_tests.py` unsandboxed.
   - Enforce **100% Pass Rate** across all 240 unit tests and 10 heavy production stress scenarios (250 total tests).

3. **Verify Documentation & Catalog Integrity**:
   - Confirm `TEST_SUITE_CATALOG.md`, `README.md`, `index.html`, and `PROD_ARCHITECTURE_REASONING.md` in all 20 projects are synchronized.

4. **Git Sync & Deployment**:
   - Stage, commit, and push all changes to GitHub (`main` branch).
   - Confirm live deployment on GitHub Pages (`https://abhi32dev.github.io/ai-infrastructure-platform/`).

---

## 3. Architecture Blueprint Standards (20 / 20 Projects)
Every project folder must contain a `PROD_ARCHITECTURE_REASONING.md` file documenting:
- Business context & real-world necessity.
- Technical decisions & architectural trade-offs (e.g. FSDP ZeRO-3 vs DeepSpeed vs DDP, PagedAttention vs static KV allocation, Triton vs CUDA C++).
- Defensive design principles (null safety, zero-copy PyArrow IPC, rate limits).
- Failure modes & automated mitigations.
