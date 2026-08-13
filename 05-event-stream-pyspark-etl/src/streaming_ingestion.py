"""
Master Event Streaming & Reconciliation Platform Orchestrator.
Integrates MIB OID Packet Decoding, TTL Idempotency Deduplication, 3-Pass Reconciliation,
and PySpark Batch Feature ETL.
"""

from typing import Any, Dict, List, Set, Tuple
from src.mib_decoder import MIBDecoder, SNMPVersion
from src.pyspark_feature_etl import PySparkFeatureETL
from src.three_pass_reconciler import ThreePassReconciler
from src.ttl_deduplicator import TTLDeduplicator


class StreamingIngestionOrchestrator:
    def __init__(self):
        print("[STREAMING ORCHESTRATOR] Initializing Event Ingestion & Reconciliation Platform...")
        self.decoder = MIBDecoder()
        self.dedup = TTLDeduplicator(default_ttl_seconds=60.0)
        self.reconciler = ThreePassReconciler()
        self.etl = PySparkFeatureETL()

    def process_incoming_packet(
        self, 
        node_id: str, 
        raw_oid: str, 
        snmp_version: SNMPVersion = SNMPVersion.SNMPv3
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Decodes incoming packet and checks TTL deduplication marker.
        Returns: (is_processed: bool, record_or_reason: Dict)
        """
        dedup_key = f"{node_id}:{raw_oid}"
        payload_hash = f"hash-{hash(raw_oid)}"

        if self.dedup.is_duplicate(dedup_key, payload_hash):
            return False, {"reason": "DUPLICATE_DROPPED_BY_TTL_MARKER", "dedup_key": dedup_key}

        alarm_rec = self.decoder.decode_packet(node_id, raw_oid, snmp_version=snmp_version)
        return True, alarm_rec.dict()

    def run_reconciliation_pass(
        self, 
        expected_files: List[str], 
        storage_listing: List[str],
        simulate_failure: bool = False
    ) -> Dict[str, Any]:
        """Runs 3-Pass Storage Reconciliation."""
        return self.reconciler.reconcile_file_delivery(
            expected_files=set(expected_files),
            simulated_storage_listing=set(storage_listing),
            simulate_partial_failure=simulate_failure
        )

    def run_batch_feature_etl(self, raw_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Runs PySpark batch aggregation ETL."""
        return self.etl.transform_and_aggregate_events(raw_events)
