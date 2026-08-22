# Interview Preparation Guide: Project 26

### 1. How to describe this project in an interview:
> "At Comcast, we received 2.4M+ daily telemetry events across 4 hardware vendors. When multi-node alarms or unclassified error traps occurred, on-call engineers spent 15–30 minutes manually correlating historical logs and MIB dictionaries. I designed a RAG-driven triage engine using AWS Bedrock (Claude 3.5 Sonnet), LangChain, and PGVector on Amazon RDS PostgreSQL that automatically matches incoming error signatures to historical post-mortems and generates root-cause diagnoses and remediation steps in under 15 seconds."

### 2. Deep-Dive Q&A:
* **Why AWS Bedrock over direct OpenAI/Anthropic API?**
  Enterprise security: Bedrock runs inside AWS VPC private endpoints with IAM authorization and strict compliance (SOC2/HIPAA), guaranteeing telemetry data never leaves AWS or gets used for public model training.
* **Why PGVector on RDS PostgreSQL?**
  Consolidates relational telemetry metadata and vector embeddings into a single managed ACID database, avoiding the operational overhead of running a separate vector-only database cluster.
