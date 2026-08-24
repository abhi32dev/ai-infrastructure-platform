# Openings Aggregator

**Openings Aggregator** is a high-performance, standalone live job aggregation system that queries public Applicant Tracking System (ATS) APIs (**Greenhouse**, **Ashby**, **Lever**) directly from your Mac.

It operates without third-party browser extensions or paid subscription services, providing a real-time dark-mode Web Dashboard with ad-hoc instruction query capabilities, full job description modals, direct ATS apply URLs, and CSV export tools.

---

## Features

- ⚡ **Direct Public API Engines**:
  - **Greenhouse Public Harvest API**: `boards-api.greenhouse.io` (*Stripe, OpenAI, Figma, Anthropic, Airbnb*)
  - **Ashby Public Board API**: `api.ashbyhq.com` (*Notion, Linear, Vercel, Scribe, Distyl*)
  - **Lever Public Postings API**: `api.lever.co` (*Spotify, Netflix, Palantir*)
- 💻 **Ad-Hoc Prompt & Instruction Bar**: Query specific keywords (e.g. `"Senior Python, AWS in San Francisco or Remote"`).
- 📄 **Full Job Description Viewer**: Modal window displaying complete, untruncated job requirements and direct ATS application links.
- 💾 **SQLite Storage & Cache**: Fast offline querying and deduplication.
- 📊 **One-Click CSV Export**: Instant export to CSV spreadsheet.

---

## Quickstart

### 1. Launch the Live Server
```bash
python3 -m backend.main
```
Open **`http://localhost:8000`** in your browser!

### 2. Run Tests
```bash
python3 -m unittest discover backend/tests
```

### 3. Run CLI Dataset Exporter
```bash
python3 export_dataset.py
```
