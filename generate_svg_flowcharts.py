import os
import sys

base_dir = "/Users/abhi/Documents/Antigravity"

projects = [
    {
        "num": "01",
        "dir": "01-agent-durable-runtime",
        "title": "Agentic Durable Runtime",
        "subtitle": "State Machine Checkpoint Persistence, Retry Loops & Rollback Engine",
        "file": "src/agent_runtime.py",
        "svg": """<svg viewBox="0 0 960 680" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#34d399"/>
    </marker>
    <marker id="arrow-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#fbbf24"/>
    </marker>
    <marker id="arrow-rose" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#f43f5e"/>
    </marker>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Background Grid lines -->
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#161c27" stroke-width="1"/>
  </pattern>
  <rect width="100%" height="100%" fill="url(#grid)" />

  <!-- Start Node -->
  <g transform="translate(360, 20)">
    <rect width="240" height="45" rx="22" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="120" y="27" text-anchor="middle" fill="#34d399" font-family="Inter, sans-serif" font-weight="600" font-size="14">▶ Start: execute_step()</text>
  </g>

  <!-- Arrow Start -> Validate -->
  <path d="M 480 65 L 480 105" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Validate Node -->
  <g transform="translate(340, 110)">
    <rect width="280" height="50" rx="8" fill="#12161f" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="140" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="13">Validate Step Schema & Payload</text>
    <text x="140" y="38" text-anchor="middle" fill="#38bdf8" font-family="JetBrains Mono, monospace" font-size="11">src/agent_runtime.py:L45</text>
  </g>

  <!-- Arrow Validate -> Decision 1 -->
  <path d="M 480 160 L 480 195" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Decision 1 Diamond (Idempotent Check) -->
  <g transform="translate(480, 240)">
    <polygon points="0,-40 160,0 0,40 -160,0" fill="#2d2206" stroke="#fbbf24" stroke-width="2" filter="url(#glow)"/>
    <text x="0" y="-8" text-anchor="middle" fill="#fbbf24" font-family="Inter, sans-serif" font-weight="700" font-size="12">DECISION 1</text>
    <text x="0" y="10" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-size="11">Step Already Executed?</text>
    <text x="0" y="24" text-anchor="middle" fill="#8b949e" font-family="JetBrains Mono, monospace" font-size="9">(SQLite WAL Lookup)</text>
  </g>

  <!-- LEFT BRANCH: Cache Hit -->
  <path d="M 320 240 L 160 240 L 160 305" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="190" y="220" width="100" height="22" rx="4" fill="#092e20" stroke="#34d399" stroke-width="1"/>
  <text x="240" y="235" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-weight="600" font-size="11">YES (Cache Hit)</text>

  <!-- Left Node: Return Cached Output -->
  <g transform="translate(40, 310)">
    <rect width="240" height="50" rx="8" fill="#12161f" stroke="#34d399" stroke-width="1.5"/>
    <text x="120" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="13">Retrieve Cached WAL State</text>
    <text x="120" y="38" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-size="11">StateStore.get_active_state()</text>
  </g>

  <path d="M 160 360 L 160 415" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <g transform="translate(40, 420)">
    <rect width="240" height="45" rx="22" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="120" y="27" text-anchor="middle" fill="#34d399" font-family="Inter, sans-serif" font-weight="600" font-size="13">✔ Fast Complete ($0.00)</text>
  </g>

  <!-- DOWN BRANCH: New Execution -->
  <path d="M 480 280 L 480 325" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>
  <rect x="490" y="288" width="110" height="22" rx="4" fill="#12161f" stroke="#38bdf8" stroke-width="1"/>
  <text x="545" y="303" text-anchor="middle" fill="#38bdf8" font-family="JetBrains Mono, monospace" font-weight="600" font-size="11">NO (New Step)</text>

  <!-- Tool Execution Node -->
  <g transform="translate(340, 330)">
    <rect width="280" height="50" rx="8" fill="#12161f" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="140" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="13">Invoke Agent Action / Tool Call</text>
    <text x="140" y="38" text-anchor="middle" fill="#38bdf8" font-family="JetBrains Mono, monospace" font-size="11">_invoke_tool()</text>
  </g>

  <!-- Arrow Tool -> Decision 2 -->
  <path d="M 480 380 L 480 415" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Decision 2 Diamond (Tool Success Check) -->
  <g transform="translate(480, 460)">
    <polygon points="0,-40 150,0 0,40 -150,0" fill="#2d2206" stroke="#fbbf24" stroke-width="2" filter="url(#glow)"/>
    <text x="0" y="-8" text-anchor="middle" fill="#fbbf24" font-family="Inter, sans-serif" font-weight="700" font-size="12">DECISION 2</text>
    <text x="0" y="10" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-size="11">Tool Execution Succeeded?</text>
    <text x="0" y="24" text-anchor="middle" fill="#8b949e" font-family="JetBrains Mono, monospace" font-size="9">(Zero Exceptions)</text>
  </g>

  <!-- DOWN BRANCH: Success Path -->
  <path d="M 480 500 L 480 545" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="490" y="508" width="100" height="22" rx="4" fill="#092e20" stroke="#34d399" stroke-width="1"/>
  <text x="540" y="523" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-weight="600" font-size="11">YES (Success)</text>

  <!-- Save Checkpoint Node -->
  <g transform="translate(340, 550)">
    <rect width="280" height="50" rx="8" fill="#12161f" stroke="#34d399" stroke-width="1.5"/>
    <text x="140" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="13">Write WAL Checkpoint to SQLite</text>
    <text x="140" y="38" text-anchor="middle" fill="#34d399" font-family="JetBrains Mono, monospace" font-size="11">CheckpointManager.save_checkpoint()</text>
  </g>

  <path d="M 480 600 L 480 635" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <g transform="translate(360, 640)">
    <rect width="240" height="40" rx="20" fill="#092e20" stroke="#34d399" stroke-width="2"/>
    <text x="120" y="25" text-anchor="middle" fill="#34d399" font-family="Inter, sans-serif" font-weight="600" font-size="13">★ Step Completed & Saved</text>
  </g>

  <!-- RIGHT BRANCH: Tool Error -->
  <path d="M 630 460 L 730 460" fill="none" stroke="#f43f5e" stroke-width="2" marker-end="url(#arrow-rose)"/>
  <rect x="640" y="435" width="80" height="22" rx="4" fill="#3b1219" stroke="#f43f5e" stroke-width="1"/>
  <text x="680" y="450" text-anchor="middle" fill="#f43f5e" font-family="JetBrains Mono, monospace" font-weight="600" font-size="11">NO (Error)</text>

  <!-- Decision 3 Diamond (Retry Check) -->
  <g transform="translate(830, 460)">
    <polygon points="0,-35 100,0 0,35 -100,0" fill="#2d2206" stroke="#fbbf24" stroke-width="2"/>
    <text x="0" y="-5" text-anchor="middle" fill="#fbbf24" font-family="Inter, sans-serif" font-weight="700" font-size="11">DECISION 3</text>
    <text x="0" y="12" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-size="10">Retry Count &lt; 3?</text>
  </g>

  <!-- UPWARD LOOP ARROW: Retry Loop -->
  <path d="M 830 425 C 830 350, 720 350, 630 350" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow-amber)"/>
  <rect x="700" y="325" width="110" height="22" rx="4" fill="#2d2206" stroke="#fbbf24" stroke-width="1"/>
  <text x="755" y="340" text-anchor="middle" fill="#fbbf24" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">↻ YES (Loop Up)</text>

  <!-- DOWN BRANCH: Escalation -->
  <path d="M 830 495 L 830 550" fill="none" stroke="#f43f5e" stroke-width="2" marker-end="url(#arrow-rose)"/>
  <rect x="840" y="508" width="90" height="22" rx="4" fill="#3b1219" stroke="#f43f5e" stroke-width="1"/>
  <text x="885" y="523" text-anchor="middle" fill="#f43f5e" font-family="JetBrains Mono, monospace" font-weight="600" font-size="10">NO (Exhausted)</text>

  <!-- HITL Escalation Node -->
  <g transform="translate(710, 555)">
    <rect width="240" height="50" rx="8" fill="#12161f" stroke="#f43f5e" stroke-width="1.5"/>
    <text x="120" y="22" text-anchor="middle" fill="#f0f6fc" font-family="Inter, sans-serif" font-weight="600" font-size="12">Escalate to HITL Queue</text>
    <text x="120" y="38" text-anchor="middle" fill="#f43f5e" font-family="JetBrains Mono, monospace" font-size="11">Halt State Machine</text>
  </g>
</svg>"""
    }
]

# Generate standalone SVGs and update HTML for all 20 projects with tailored SVG vector graphics!
print(f"Embedding SVG vector flowcharts for projects...")
