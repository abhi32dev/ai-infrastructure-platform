# 📡 Project 5: Event Streaming, PySpark ETL & 3-Pass Reconciliation Engine

A production-grade, local-first **Real-Time Data & Feature Ingestion Engine** implementing persistent UDP socket trap listeners, vendor MIB OID decoding, DynamoDB-style TTL idempotency markers, Comcast CONDOR 3-Pass Storage Reconciliation, and PySpark distributed batch feature ETL pipelines.

---

## 🎯 Resume & Architecture Mapping

| Feature / Architectural Pattern | Resume Claim Mapped | Implementation Module |
| :--- | :--- | :--- |
| **Multi-Protocol MIB Decoder** | Persistent UDP trap receivers, SNMPv1/v2c/v3 auth | [`src/mib_decoder.py`](src/mib_decoder.py) |
| **TTL Idempotency Deduplication**| DynamoDB TTL-keyed per-file dedup markers | [`src/ttl_deduplicator.py`](src/ttl_deduplicator.py) |
| **3-Pass Storage Reconciliation** | S3 listing diff-and-retry & raw recovery pass | [`src/three_pass_reconciler.py`](src/three_pass_reconciler.py) |
| **Distributed PySpark Feature ETL** | PySpark batch data transformation & Snowflake staging | [`src/pyspark_feature_etl.py`](src/pyspark_feature_etl.py) |

---

## 📁 Repository Structure

```text
05-event-stream-pyspark-etl/
├── src/
│   ├── mib_decoder.py            # MIB OID decoder (severity, probable cause, alarm type, SNMPv1/v2c/v3)
│   ├── ttl_deduplicator.py       # TTL-keyed deduplication marker & collision avoidance engine
│   ├── three_pass_reconciler.py  # 3-Pass Reconciliation (Pass 1: initial, Pass 2: S3 retry, Pass 3: raw recovery)
│   ├── pyspark_feature_etl.py    # PySpark batch feature transformation & Snowflake staging
│   └── streaming_ingestion.py    # Master Streaming Ingestion & Reconciliation Orchestrator
├── tests/
│   └── test_event_pipeline.py    # Pytest test suite for MIB decoding, TTL dedup, 3-pass reconciler, and PySpark ETL
├── app.py                        # FastAPI REST API & embedded Real-Time Ingestion Dashboard
├── demo_runner.py                # Interactive CLI script running 4 core event streaming scenarios
├── requirements.txt              # Project dependencies
├── README.md                     # System documentation
└── INTERVIEW_PREP.md             # Staff AI Infra / Data Engineering Interview Guide
```

---

## 🚦 Quick Start & Interactive Demo

### 1. Run the Interactive CLI Demo
```bash
python3 demo_runner.py
```
This executes 4 core production scenarios:
- **Scenario 1**: Persistent UDP MIB OID Trap Packet Decoding (SNMPv3 auth).
- **Scenario 2**: TTL-Based Idempotency Deduplication.
- **Scenario 3**: Three-Pass Storage Reconciliation (recovering from simulated partial S3 upload failures).
- **Scenario 4**: PySpark Distributed Batch Aggregation ETL.

### 2. Run Pytest Suite
```bash
pytest tests/
```

### 3. Launch FastAPI Server & Ingestion Dashboard
```bash
python3 app.py
```
Then open your browser to **http://127.0.0.1:8004** to ingest trap packets, trigger 3-pass reconciliation, and view PySpark ETL aggregations!
