# Project 28: FastAPI Pydantic v2 Schema Governance

Production-grade implementation of **Pydantic v2 Strict Schema Governance, OpenAPI 3.1 Contracts, and Polymorphic Webhook Ingestion** on FastAPI / Amazon ECS Fargate.

---

## 🏗️ Architecture Overview

```
[ Ingested Multi-Vendor Webhooks ] (Google SAS / Nokia / Samsung)
               │
               ▼
[ FastAPI + Pydantic v2 Core (Rust Engine) ]
               │
               ├──► [ Discriminated Polymorphic Validator ]
               ├──► [ Boundary Value Regex & Range Constraints ]
               └──► [ Cross-Item Invariant Checkers (@model_validator) ]
               │
               ▼
    [ Clean, Typed Internal Events ] ──► [ Kinesis / ECS Backend ]
```

---

## 🚀 Key Production Capabilities

1. **Rust-Core Speedup:** Pydantic v2 provides a 5x–20x serialization/validation throughput increase over v1, essential for multi-million event pipelines.
2. **Polymorphic Discriminated Unions:** Dynamically dispatches complex JSON payloads to vendor-specific schemas (e.g. `GOOGLE_SAS`, `NOKIA`, `SAMSUNG`) with zero boilerplate `if/else` ladders.
3. **Strict Validation Boundaries:** Rejects malformed payload keys (`extra="forbid"`), enforcing zero runtime schema drift across microservice fleets.

---

## 🧪 Testing

```bash
cd 28-fastapi-pydantic-schema-governance
pytest tests/ -v
```
