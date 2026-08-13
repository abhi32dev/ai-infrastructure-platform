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

1. **Mandatory Visual Self-Evaluation & Screenshot UAT**:
   - Whatever UI, HTML page, or diagram is designed, ALWAYS render/inspect the output visual image first before pushing.
   - Act as your own self-evaluator. Verify that text contrast, multi-directional arrows, decision diamonds, process boxes, and code signatures are 100% visible, non-broken, and crisp.
   - Only when it passes visual UAT and looks exceptional, proceed to push to Git!

2. **Verify All Project Links in `index.html`**:
   - Ensure every project tile/card is fully clickable and links to valid GitHub repository tree URLs (`https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/<project_dir>`).
   - Ensure all `Blueprint →` links correctly resolve to `https://github.com/abhi32dev/ai-infrastructure-platform/blob/main/<project_dir>/PROD_ARCHITECTURE_REASONING.md`.
   - Test that clicking anywhere on the tile card cleanly opens the project directory.

3. **Execute Full Test Suite Verification**:
   - Run `python3 tests/run_all_20_project_tests.py` unsandboxed.
   - Enforce **100% Pass Rate** across all 240 unit tests and 10 heavy production stress scenarios (250 total tests).

4. **Verify Documentation & Catalog Integrity**:
   - Confirm `TEST_SUITE_CATALOG.md`, `README.md`, `index.html`, and `PROD_ARCHITECTURE_REASONING.md` in all 20 projects are synchronized.

5. **Git Sync & Deployment**:
   - Stage, commit, and push all changes to GitHub (`main` branch).
   - Confirm live deployment on GitHub Pages (`https://abhi32dev.github.io/ai-infrastructure-platform/`).

---

## 3. Architecture Blueprint Standards (20 / 20 Projects)
Every project folder must contain a `PROD_ARCHITECTURE_REASONING.md` file documenting:
- Business context & real-world necessity.
- Technical decisions & architectural trade-offs (e.g. FSDP ZeRO-3 vs DeepSpeed vs DDP, PagedAttention vs static KV allocation, Triton vs CUDA C++).
- Defensive design principles (null safety, zero-copy PyArrow IPC, rate limits).
- Failure modes & automated mitigations.

---

## 4. Visual 2D Flowchart Architecture Standards
- All flowcharts must be embedded as **NATIVE INLINE SVG AND PURE HTML/CSS 2D DIAGRAM CARDS** directly inside `FLOWCHART.html` (NO `<img src="...">` tags, zero broken image icons).
- **NO Background Grid Lines**: Solid dark canvas background (`#0d1117`).
- **100% Crisp High-Contrast Vector Graphics**: High-contrast process boxes (`fill="#161b22"` with `#38bdf8` or `#34d399` borders, white text `#ffffff`), gold decision diamonds (`#1f1906` fill, `#fbbf24` border, white text), and explicit multi-directional arrowheads.
- **Executive Architecture Cards Below**: Include exact file/function signatures, rule evaluated, and directional route cards (`↙ LEFT FAST-PATH`, `↓ DOWN EXECUTION`, `↘ RIGHT EXCEPTION`, `↺ UPWARD RETRY LOOP`).

---

## 5. Strict Self-Evaluation & Zero Broken Image Guarantee
- **NEVER assume a design passed UAT without inspecting the rendered output**.
- **NEVER use external `<img src="...">` tags inside `FLOWCHART.html`**. If an image fails to load or CDN cache is delayed, it renders a broken icon box (`[2D Control Flow Architecture Diagram]`).
- **ALWAYS use 100% self-contained native HTML5 + CSS3 elements + inline SVG** inside `FLOWCHART.html`. PURE HTML/CSS layout CANNOT produce broken image icons and will ALWAYS render cleanly in every browser under all network conditions.
