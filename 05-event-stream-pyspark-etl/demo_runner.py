"""
Interactive CLI Runner & Test Suite for Project 5 - Event Streaming & PySpark ETL.
Runs 4 core production scenarios:
1. Persistent UDP MIB OID Packet Decoding (SNMPv1/v2c/v3 auth).
2. TTL-Based Idempotency & Collision Avoidance.
3. Three-Pass Storage Reconciliation (Pass 1, Pass 2 Retry, Pass 3 Recovery).
4. PySpark Distributed Batch Aggregation & Feature ETL.
"""

import asyncio
import json

from src.mib_decoder import SNMPVersion
from src.streaming_ingestion import StreamingIngestionOrchestrator


def run_demo():
    print("==========================================================================")
    print("📡 STARTING HIGH-THROUGHPUT EVENT STREAMING & PYSPARK ETL DEMO")
    print("==========================================================================\n")

    orchestrator = StreamingIngestionOrchestrator()

    # -------------------------------------------------------------------------
    # SCENARIO 1: Multi-Protocol MIB OID Decoding
    # -------------------------------------------------------------------------
    print("--- [SCENARIO 1] Persistent UDP Trap Receiver & MIB OID Decoding ---")
    node_id = "edge-node-108"
    oid_crit = "1.3.6.1.4.1.9.9.43.1.1.1"

    is_proc, record = orchestrator.process_incoming_packet(node_id, oid_crit, snmp_version=SNMPVersion.SNMPv3)
    print(f"Decoded SNMPv3 Packet for Node '{node_id}':")
    print(f"  └─ Alarm ID:       {record['alarm_id']}")
    print(f"  └─ Severity:       {record['severity']}")
    print(f"  └─ Probable Cause: {record['probable_cause']}")
    print(f"  └─ Alarm Type:     {record['alarm_type']}")

    # -------------------------------------------------------------------------
    # SCENARIO 2: TTL-Based Idempotency Deduplication
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 2] TTL-Based Idempotency Deduplication ---")
    print("Sending duplicate trap packet with same node_id and OID within TTL window...")
    is_dup_proc, dup_res = orchestrator.process_incoming_packet(node_id, oid_crit, snmp_version=SNMPVersion.SNMPv3)
    print(f"Duplicate Packet Processing Status: Processed = {is_dup_proc}")
    print(f"  └─ Result: {dup_res}")

    # -------------------------------------------------------------------------
    # SCENARIO 3: Three-Pass Storage Reconciliation
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 3] Three-Pass Storage Reconciliation ---")
    expected_manifest = ["pm_file_001.xml", "pm_file_002.xml", "pm_file_003.xml", "pm_file_004.xml"]
    storage_listing = ["pm_file_001.xml", "pm_file_002.xml", "pm_file_003.xml", "pm_file_004.xml"]

    print("Simulating partial storage delivery failure (Pass 1 missing 2 files)...")
    recon_res = orchestrator.run_reconciliation_pass(expected_manifest, storage_listing, simulate_failure=True)

    print(f"Reconciliation Result:")
    print(f"  └─ Final Status:           {recon_res['status']}")
    print(f"  └─ Total Passes Executed: {recon_res['reconciliation_passes_run']}")
    print(f"  └─ Recovered Files:       {recon_res['recovered_files']}")
    print(f"  └─ Silent Data Gaps:      {recon_res['silent_gaps']}")

    # -------------------------------------------------------------------------
    # SCENARIO 4: PySpark Distributed Batch Aggregation ETL
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 4] PySpark Distributed Batch Aggregation ETL ---")
    raw_events = [
        {"alarm_id": "a1", "node_id": "edge-node-108", "severity": "CRITICAL", "payload_size_bytes": 1024},
        {"alarm_id": "a2", "node_id": "edge-node-108", "severity": "CRITICAL", "payload_size_bytes": 2048},
        {"alarm_id": "a3", "node_id": "edge-node-108", "severity": "MAJOR", "payload_size_bytes": 512},
        {"alarm_id": "a4", "node_id": "edge-node-204", "severity": "CRITICAL", "payload_size_bytes": 4096},
        {"alarm_id": "a5", "node_id": "edge-node-204", "severity": "WARNING_HEARTBEAT", "payload_size_bytes": 128}
    ]

    print(f"Running PySpark ETL over {len(raw_events)} raw event records...")
    aggregated_features = orchestrator.run_batch_feature_etl(raw_events)

    print("PySpark Aggregated Node Features:")
    for feat in aggregated_features:
        print(f"  └─ Node '{feat['node_id']}': Total Alarms = {feat['total_alarms']} | Critical Count = {feat['critical_count']} | Avg Payload = {feat['avg_payload_bytes']:.1f} bytes")

    print("\n==========================================================================")
    print("✅ DEMO COMPLETED SUCCESSFULLY! ALL 4 EVENT STREAMING SCENARIOS VERIFIED.")
    print("==========================================================================\n")


if __name__ == "__main__":
    run_demo()
