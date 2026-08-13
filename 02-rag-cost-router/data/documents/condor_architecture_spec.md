# Comcast CONDOR Edge Node Ingestion & Socket Receiver Architecture

## 1. System Overview
The Comcast CONDOR platform processes telemetry events from over 12,000 edge nodes across 108 million active devices, sustaining a daily throughput of 2.4 million events with 99.999% SLA availability.

## 2. Persistent Socket Receiver & UDP Trap Daemon
Edge telemetry traps arrive via SNMPv1/v2c/v3 packets over UDP port 162. To handle spike volume without dropping packets:
- Dedicated Dockerized Python daemons run on Amazon EC2 instances inside a Private App VPC Subnet.
- Sockets use `SO_REUSEPORT` kernel socket options for multi-core parallel trap ingestion.
- DynamoDB TTL markers provide 300-second window deduplication for incoming event payloads.

## 3. Storage & 3-Pass Storage Reconciliation
To eliminate silent data gaps across AWS S3 storage buckets:
- **Pass 1 (Parallel Ingestion)**: Real-time streaming pass writes incoming decoded MIB payloads directly to S3.
- **Pass 2 (Diff & Retry Reconciliation)**: A hourly batch job lists S3 bucket prefixes, identifies missing file keys against DynamoDB transaction logs, and triggers automated replay retries.
- **Pass 3 (Raw Edge Recovery)**: An emergency recovery pass extracts raw unparsed binary logs directly from host EC2 NVMe buffer drives if S3 endpoint outages occur.
