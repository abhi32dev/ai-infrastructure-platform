# 🎤 Staff AI Platform Interview Guide: Event Stream PySpark ETL & Delta Lake

This guide bridges **Project 5 (`05-event-stream-pyspark-etl`)** to Staff/Principal-level questions on streaming architectures and Delta Lake ACID transactions.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you handle late-arriving streaming data and deduplication in PySpark Structured Streaming?"
> **Staff Engineer Answer**:
> "In `src/event_pipeline.py`, we apply a 10-minute event watermark boundary (`withWatermark('event_timestamp', '10 minutes')`). Late records past the watermark are dropped, and `dropDuplicates(['event_id'])` eliminates duplicate events."

### Q2: "How do Delta Lake Gold tables enforce ACID transaction guarantees during streaming ingestion?"
> **Staff Engineer Answer**:
> "Delta Lake uses atomic commit logs (`_delta_log/`) with optimistic concurrency control. Each streaming micro-batch commits atomically as a new version snapshot, preventing partial reads."

### Q3: "How do you isolate corrupted telemetry payloads without halting streaming jobs?"
> **Staff Engineer Answer**:
> "Records failing schema validation are routed to an S3 Dead-Letter Queue (DLQ) bucket, allowing healthy micro-batches to commit while quarantined records trigger OpenLineage alerting."
