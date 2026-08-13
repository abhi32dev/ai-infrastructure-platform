# 🎤 Staff / Principal AI Infrastructure & Data Systems Interview Guide

This guide bridges the code in **Project 5 (`05-event-stream-pyspark-etl`)** directly to Staff/Principal-level questions asked by FAANG, Tier-1 AI startups, and top product companies.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "Why run persistent EC2 daemons instead of AWS Lambda for high-volume network ingestion?"
> **Staff Engineer Answer**:
> "AWS Lambda is a request-driven, short-lived execution model (max 15-minute execution time) designed for statestore HTTP triggers.
> 
> Network protocols like SNMP trap receivers require holding a persistent listening socket open on UDP port 162 across an unbounded connection lifetime. You cannot hold open a persistent UDP listening socket inside a request-driven Lambda.
> 
> In `05-event-stream-pyspark-etl`, we ran persistent Dockerized Python daemons on Amazon EC2 instances behind a Network Load Balancer ([`src/mib_decoder.py`](src/mib_decoder.py)). Each daemon loads vendor MIB modules to decode incoming traps into OID-mapped severity and probable cause across SNMPv1, SNMPv2c, and SNMPv3 (SHA/AES) authentication simultaneously."

---

### Q2: "How do you guarantee zero silent data gaps across thousands of edge node files?"
> **Staff Engineer Answer**:
> "Relying purely on in-memory success flags or single-pass HTTP upload triggers inevitably leads to silent data gaps during network blips. We implemented the **Three-Pass Reconciliation Algorithm** ([`src/three_pass_reconciler.py`](src/three_pass_reconciler.py)):
> 
> - **Pass 1 (Initial Parallel Ingestion Pass)**: Slices directory listings and triggers parallel worker ingestion.
> - **Pass 2 (S3 Storage Listing Diff-and-Retry Loop)**: Queries actual S3 bucket listings, diffs them against expected manifest keys, and re-invokes missing files up to 3 times.
> - **Pass 3 (Raw-File Recovery Pass)**: Executes a dedicated raw-file fetch directly from the source SFTP storage for any unhealed partial failures.
> 
> This three-tier contract self-heals partial failures within the same 30-minute cycle without surfacing silent data gaps to downstream analytics or ML feature stores."

---

### Q3: "How do you prevent double-counting when events are retried across distributed consumer nodes?"
> **Staff Engineer Answer**:
> "We implement **TTL-Based Idempotency Markers** ([`src/ttl_deduplicator.py`](src/ttl_deduplicator.py)).
> 
> Before processing an incoming event or file payload, the worker computes a deterministic deduplication key (`node_id:raw_oid` or `file_archive_hash`) and checks a TTL-keyed table. 
> 
> If the key exists within an active 300-second TTL window, the duplicate delivery is cleanly dropped before updating downstream counters or writing to S3. This guarantees idempotency across concurrent multi-node writes."

---

## 🧪 Quick Test Checklist for Candidates
Run these commands in your workspace to test and demonstrate:
- `python3 demo_runner.py`: Executes all 4 event streaming and reconciliation scenarios live.
- `pytest tests/`: Verifies unit and integration test suite.
- `python3 app.py`: Opens Ingestion Dashboard at `http://127.0.0.1:8004` to visually send trap packets, test 3-pass reconciliation, and view PySpark ETL aggregations.
