"""
Expanded Test Suite for Project 5 - Event Stream & PySpark ETL.
Tests MIB OID packet decoding, DynamoDB TTL deduplication, PySpark feature transformations,
and Comcast CONDOR 3-Pass Storage Reconciliation (Pass 1 Stream, Pass 2 Diff/Retry, Pass 3 NVMe Recovery).
"""

import pytest
from src.mib_decoder import MIBDecoder, AlarmSeverity, SNMPVersion
from src.ttl_deduplicator import TTLDeduplicator
from src.pyspark_feature_etl import PySparkFeatureETL
from src.three_pass_reconciler import ThreePassReconciler


@pytest.fixture
def decoder():
    return MIBDecoder()


@pytest.fixture
def dedup():
    return TTLDeduplicator(default_ttl_seconds=300.0)


@pytest.fixture
def reconciler():
    return ThreePassReconciler()


def test_01_snmp_packet_decoder_oid_parsing(decoder):
    """Test 1: Verifies SNMP trap MIB OID parsing for enterprise edge node metrics."""
    record = decoder.decode_packet(
        node_id="edge-node-108",
        raw_oid="1.3.6.1.4.1.9.9.43.1.1.1",
        snmp_version=SNMPVersion.SNMPv3,
        auth_pass="sha_aes_key"
    )
    assert record.severity == AlarmSeverity.CRITICAL
    assert record.probable_cause == "High CPU Temperature Pressure"
    assert record.node_id == "edge-node-108"


def test_02_dynamodb_ttl_deduplication(dedup):
    """Test 2: Verifies DynamoDB 300-second window event deduplication logic."""
    event_key = "evt-node-108-999"
    payload_hash = "hash_abc_123"
    
    assert dedup.is_duplicate(event_key, payload_hash) is False  # First time -> not duplicate
    assert dedup.is_duplicate(event_key, payload_hash) is True   # Second time -> duplicate!


def test_03_pyspark_feature_transformation_aggregations():
    """Test 3: Verifies PySpark feature transformation aggregations."""
    engine = PySparkFeatureETL()
    raw_events = [
        {"node_id": "node-108", "severity": "CRITICAL", "payload_size_bytes": 128},
        {"node_id": "node-108", "severity": "MINOR", "payload_size_bytes": 64},
        {"node_id": "node-109", "severity": "CRITICAL", "payload_size_bytes": 256}
    ]
    df_res = engine.transform_and_aggregate_events(raw_events)
    assert len(df_res) == 2
    node_108_stats = [r for r in df_res if r["node_id"] == "node-108"][0]
    assert node_108_stats["total_alarms"] == 2
    assert node_108_stats["critical_count"] == 1


def test_04_storage_reconciliation_pass_1_success(reconciler):
    """Test 4: Verifies Pass 1 real-time streaming ingestion success."""
    expected_files = {"file1.parquet", "file2.parquet"}
    storage_files = {"file1.parquet", "file2.parquet"}
    res = reconciler.reconcile_file_delivery(expected_files, storage_files, simulate_partial_failure=False)
    assert res["status"] == "SUCCESS_PASS_1"
    assert res["reconciliation_passes_run"] == 1


def test_05_storage_reconciliation_pass_2_diff_retry(reconciler):
    """Test 5: Verifies Pass 2 storage listing diff & retry reconciliation."""
    expected_files = {"file1.parquet", "file2.parquet"}
    storage_files = {"file1.parquet"}
    res = reconciler.reconcile_file_delivery(expected_files, storage_files, simulate_partial_failure=False)
    assert res["status"] == "HEALED_IN_PASS_2"
    assert res["reconciliation_passes_run"] == 2


def test_06_storage_reconciliation_pass_3_raw_recovery(reconciler):
    """Test 6: Verifies Pass 3 raw-file recovery pass during storage outages."""
    expected_files = {"f1.parquet", "f2.parquet", "f3.parquet", "f4.parquet", "f5.parquet"}
    storage_files = {"f1.parquet"}
    res = reconciler.reconcile_file_delivery(expected_files, storage_files, simulate_partial_failure=True)
    assert res["status"] == "HEALED_IN_PASS_3"
    assert res["reconciliation_passes_run"] == 3


def test_07_snmpv3_auth_failure(decoder):
    """Test 7: Verifies SNMPv3 authentication failure when security key is missing."""
    with pytest.raises(PermissionError):
        decoder.decode_packet(
            node_id="edge-108",
            raw_oid="1.3.6.1.4.1.9.9.43.1.1.1",
            snmp_version=SNMPVersion.SNMPv3,
            auth_pass=None
        )


def test_08_high_volume_event_burst_deduplication(dedup):
    """Test 8: Verifies deduplicator under high-volume event stream burst."""
    for i in range(50):
        dedup.is_duplicate(f"evt-{i}", f"hash-{i}")
    assert dedup.is_duplicate("evt-25", "hash-25") is True
    assert dedup.is_duplicate("evt-999", "hash-999") is False


def test_09_mib_decoder_unknown_oid(decoder):
    """Test 9 [Production Edge Case]: Verifies MIB decoder handling unknown OIDs with default MINOR severity."""
    rec = decoder.decode_packet("node-unknown", raw_oid="1.3.6.1.99.99")
    assert rec.severity == AlarmSeverity.MINOR



def test_10_pyspark_etl_empty_events_list():
    """Test 10 [Production Edge Case]: Verifies PySpark feature ETL handling empty input event list cleanly."""
    engine = PySparkFeatureETL()
    df_res = engine.transform_and_aggregate_events([])
    assert len(df_res) == 0


def test_11_ttl_deduplicator_expired_window(dedup):
    """Test 11 [Production Edge Case]: Verifies TTL deduplicator expiring entries after TTL seconds."""
    dedup_short = TTLDeduplicator(default_ttl_seconds=0.01)
    dedup_short.is_duplicate("key-1", "hash-1")
    import time
    time.sleep(0.02)
    assert dedup_short.is_duplicate("key-1", "hash-1") is False  # Expired -> allowed again!


def test_12_reconciler_empty_expected_files(reconciler):
    """Test 12 [Production Edge Case]: Verifies 3-pass reconciler handling empty expected file set."""
    res = reconciler.reconcile_file_delivery(set(), set())
    assert res["status"] == "SUCCESS_PASS_1"

