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
   - Whatever UI, HTML page, or diagram is designed, ALWAYS inspect the output visual and XML validity first before pushing.
   - Act as your own self-evaluator. Verify that text contrast, multi-directional arrows, decision diamonds, process boxes, and code signatures are 100% visible, non-broken, and crisp.
   - Only when it passes visual UAT and looks exceptional, proceed to push to Git!

2. **Verify All Project Links in `index.html`**:
   - Ensure every project tile/card is fully clickable and links to valid GitHub repository tree URLs (`https://github.com/abhi32dev/ai-infrastructure-platform/tree/main/<project_dir>`).
   - Ensure all `Blueprint →` links correctly resolve to `https://github.com/abhi32dev/ai-infrastructure-platform/blob/main/<project_dir>/PROD_ARCHITECTURE_REASONING.md`.
   - Test that clicking anywhere on the tile card cleanly opens the project directory.

3. **Execute Full Test Suite Verification**:
   - Run `python3 tests/run_all_20_project_tests.py`, `tests/run_all_25_project_tests.py` unsandboxed, and project 32 tests.
   - Enforce **100% Pass Rate** across all 402 verified unit and integration test targets.

4. **Verify Documentation & Catalog Integrity**:
   - Confirm `TEST_SUITE_CATALOG.md`, `README.md`, `index.html`, `INTERVIEW_PREP.md`, and `PROD_ARCHITECTURE_REASONING.md` across all 27 projects are synchronized.

5. **Git Sync & Deployment**:
   - Stage, commit, and push all changes to GitHub (`main` branch).
   - Confirm live deployment on GitHub Pages (`https://abhi32dev.github.io/ai-infrastructure-platform/`).

---

## 3. Architecture Blueprint Standards (27 / 27 Projects)
Every project folder must contain a `PROD_ARCHITECTURE_REASONING.md` file documenting:
- Business context & real-world necessity.
- Technical decisions & architectural trade-offs (e.g. FSDP ZeRO-3 vs DeepSpeed vs DDP, PagedAttention vs static KV allocation, Triton vs CUDA C++, Multi-LoRA vs single-tenant, Disaggregated Prefill/Decode vs colocated, FP8 vs FP16, NCCL Ring vs Tree).
- Defensive design principles (null safety, zero-copy PyArrow IPC, rate limits).
- Failure modes & automated mitigations.
- **Section 5: End-to-End Operational Manual & Step-by-Step Execution Guide**.

---

## 4. Visual 2D Flowchart Architecture Standards
- All flowcharts must be embedded as **NATIVE INLINE SVG AND PURE HTML/CSS 2D DIAGRAM CARDS** directly inside `FLOWCHART.html` (NO `<img src="...">` tags, zero broken image icons).
- **NO Background Grid Lines**: Solid dark canvas background (`#0d1117`).
- **100% Crisp High-Contrast Vector Graphics**: High-contrast process boxes (`fill="#161b22"` with `#38bdf8` or `#34d399` borders, white text `#ffffff`), gold decision diamonds (`#1f1906` fill, `#fbbf24` border, white text), and explicit multi-directional arrowheads.
- **Executive Architecture Cards Below**: Include exact file/function signatures, rule evaluated, and directional route cards (`↙ LEFT FAST-PATH`, `↓ DOWN EXECUTION`, `↘ RIGHT EXCEPTION`, `↺ UPWARD RETRY LOOP`).

---

## 5. Strict Self-Evaluation & Zero Broken Image Guarantee
- **NEVER assume a design passed UAT without inspecting the rendered output**.
- **NEVER use external `<img src="...">` tags inside `FLOWCHART.html`**. If an image fails to load or CDN cache is delayed, it renders a broken icon box.
- **ALWAYS use 100% self-contained native HTML5 + CSS3 elements + inline SVG** inside `FLOWCHART.html`. PURE HTML/CSS layout CANNOT produce broken image icons and will ALWAYS render cleanly in every browser under all network conditions.

---

## 6. Resume Generation & Versioning Protocols
- **Always Increment Version by 0.1**: For any new generation/iteration of the resume, increment the minor version by `0.1` (Current: `v2.0` → Next: `v2.1` → `v2.2` → `v2.3`, etc.).
- **Primary Storage Location**: Save compiled PDFs directly to:
  `/Users/abhi/Library/CloudStorage/OneDrive-SharedLibraries-oneDrive/2026/Resume/Cloud_BEDev/Gemini/Staff_Principal_Resume_v<X.Y>.pdf`
- **Dual Delivery (PDF + Antigravity Side Artifact)**:
  1. Compile the exact 2-page PDF.
  2. Render high-res PNG pages and update the **side-panel artifact** (`Staff_Principal_Resume.md`) so the user can visually view the document inside the Antigravity app with one click.
  3. Always output the full absolute path in a single-line text code block for one-click copying.

