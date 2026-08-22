# Project 26: AWS Bedrock RAG Telemetry Triage & Multi-Agent Swarm

Production-grade implementation of the **Comcast CONDOR AI Telemetry Triage Engine**, demonstrating how **AWS Bedrock (Claude 3.5 Sonnet)**, **LangChain**, **PGVector on Amazon RDS PostgreSQL**, and **Multi-Agent Pytest Synthesis** are integrated into a high-scale distributed edge automation platform.

---

## 🏗️ Architecture Overview

```
[ Edge Hardware Fleet ] (Google SAS, Federated Wireless, Samsung, Nokia)
       │
       ├── [ UDP Port 162 Traps ] ──────────────► [ AWS Network Load Balancer (NLB) ]
       │                                                      │
       │                                            [ EC2 Receiver Fleet (pysnmp) ]
       │                                                      │
       │                                            [ Amazon SQS Ingestion Buffer ]
       │                                                      │
       └── [ HTTP/REST Webhooks ] ──────────────► [ Application Load Balancer (ALB) ]
                                                              │
                                                    [ ECS/Fargate Microservices ]
                                                              │
                                            ┌─────────┴────────────────────────┐
                                            ▼                                  ▼
                               [ Kinesis Data Streams ]            [ Amazon DynamoDB ]
                                            │                      (Atomic Dedup & TTL)
                                            ▼                                  │
                               [ Lambda Event Processors ]                     │
                                            │                                  │
                                            ▼                                  ▼
                              [ AWS Bedrock + LangChain ] ◄──► [ Amazon RDS (PGVector) ]
                                            │                  (Historical Runbooks RAG)
                                            ▼
                              [ Automated Incident Triage ] ──► [ ServiceNow / Jira / SRE ]
```

---

## 🚀 Key Production Capabilities

1. **RAG Telemetry Triage:** Ingests unclassified multi-vendor error traps, executes cosine similarity search against PGVector incident runbooks, and synthesizes root-cause diagnoses via AWS Bedrock.
2. **Pydantic v2 Schema Governance:** Enforces strict typing, JSON serialization, and OpenAPI contracts across all microservices.
3. **Multi-Agent Developer Velocity Swarm:** Automates Pytest matrix synthesis and PR review compliance to act as an engineering force multiplier.
4. **Resilient Fallback:** Provides zero-exception deterministic fallback if AWS Bedrock API rate limits or network partitions occur.

---

## 🧪 Running Automated Tests

```bash
cd 26-aws-bedrock-rag-telemetry-triage
pytest tests/ -v
```
