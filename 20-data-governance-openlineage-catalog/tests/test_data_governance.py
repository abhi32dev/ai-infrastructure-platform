"""
Expanded Test Suite for Project 20 - Data Governance & OpenLineage Catalog.
Includes production edge cases for missing schema fields, zero-record contract validations, and multi-node lineage graphs.
"""

import pytest
from src.openlineage_emitter import OpenLineageEmitter
from src.marquez_lineage import MarquezLineageTracker
from src.data_contract_validator import DataContractValidator
from src.governance_orchestrator import DataGovernanceOrchestrator


@pytest.fixture
def emitter():
    return OpenLineageEmitter()


@pytest.fixture
def lineage():
    return MarquezLineageTracker()


@pytest.fixture
def validator():
    return DataContractValidator(required_fields=["entity_id", "timestamp", "payload"])


@pytest.fixture
def orchestrator():
    return DataGovernanceOrchestrator()


def test_01_openlineage_event_emission(emitter):
    """Test 1: Verifies OpenLineage event emission schema (START/COMPLETE)."""
    event = emitter.emit_job_event("COMPLETE", "pyspark_etl_job", "run-101", ["raw_logs"], ["features_table"])
    assert event.event_type == "COMPLETE"
    assert event.job_name == "pyspark_etl_job"
    assert len(event.inputs) == 1
    assert len(emitter.emitted_events) == 1


def test_02_marquez_lineage_graph_building(lineage):
    """Test 2: Verifies Marquez dataset lineage dependency graph construction."""
    lineage.record_job_lineage("job_1", ["dataset_A"], ["dataset_B"])
    graph = lineage.export_graph_summary()
    assert graph.total_datasets == 2
    assert graph.total_jobs == 1
    assert "dataset_A -> [job_1]" in graph.lineage_edges
    assert "[job_1] -> dataset_B" in graph.lineage_edges


def test_03_data_contract_validation_pass(validator):
    """Test 3: Verifies data quality contract validation passing on compliant records."""
    records = [
        {"entity_id": "e-1", "timestamp": 1000.0, "payload": "data"},
        {"entity_id": "e-2", "timestamp": 1001.0, "payload": "data"}
    ]
    res = validator.validate_dataset_batch(records)
    assert res.is_valid is True
    assert res.quality_score_pct == 100.0
    assert len(res.contract_violations) == 0


def test_04_data_contract_validation_fail(validator):
    """Test 4: Verifies data contract detecting missing required schema fields."""
    records = [
        {"entity_id": "e-1", "timestamp": 1000.0, "payload": "data"},
        {"entity_id": "e-2"}  # Missing timestamp and payload!
    ]
    res = validator.validate_dataset_batch(records)
    assert res.is_valid is False
    assert res.quality_score_pct == 50.0
    assert len(res.contract_violations) == 2


def test_05_orchestrator_governance_pipeline_pass(orchestrator):
    """Test 5: Verifies end-to-end data governance pipeline execution on valid batch."""
    records = [{"entity_id": "e-1", "timestamp": 100.0, "payload": "raw"}]
    res = orchestrator.run_governance_pipeline("etl_clean_job", records)
    assert res["status"] == "GOVERNANCE_PASSED"
    assert res["openlineage_event_type"] == "COMPLETE"
    assert len(res["lineage_edges"]) > 0


def test_06_orchestrator_governance_pipeline_blocked(orchestrator):
    """Test 6: Verifies governance pipeline blocking job execution when contract fails."""
    records = [{"bad_field": 123}]  # Fails contract!
    res = orchestrator.run_governance_pipeline("etl_clean_job", records)
    assert res["status"] == "DATA_CONTRACT_VIOLATION"
    assert len(res["violations"]) > 0


def test_07_empty_record_batch_validation(validator):
    """Test 7: Verifies data contract validator handling empty record batch."""
    res = validator.validate_dataset_batch([])
    assert res.is_valid is True
    assert res.total_records_checked == 0


def test_08_lineage_tracker_multi_job_graph(lineage):
    """Test 8: Verifies multi-stage data pipeline lineage graph tracking."""
    lineage.record_job_lineage("stage_1", ["raw"], ["inter"])
    lineage.record_job_lineage("stage_2", ["inter"], ["final"])
    graph = lineage.export_graph_summary()
    assert graph.total_datasets == 3
    assert graph.total_jobs == 2


def test_09_openlineage_fail_event_type(emitter):
    """Test 9 [Production Edge Case]: Verifies emitting FAIL status OpenLineage events."""
    event = emitter.emit_job_event("FAIL", "failed_job", "run-99", ["input_table"], ["failed_output"])
    assert event.event_type == "FAIL"


def test_10_validator_none_value_rejection(validator):
    """Test 10 [Production Edge Case]: Verifies data contract validator detecting explicit None/null values in required fields."""
    records = [{"entity_id": "e-1", "timestamp": None, "payload": "data"}]  # timestamp is None!
    res = validator.validate_dataset_batch(records)
    assert res.is_valid is False
    assert "timestamp" in res.contract_violations[0]


def test_11_lineage_tracker_empty_summary(lineage):
    """Test 11 [Production Edge Case]: Verifies Marquez lineage summary on empty tracker."""
    graph = lineage.export_graph_summary()
    assert graph.total_datasets == 0
    assert graph.total_jobs == 0
    assert len(graph.lineage_edges) == 0


def test_12_orchestrator_multi_input_datasets(orchestrator):
    """Test 12 [Production Edge Case]: Verifies governance pipeline handling multi-input dataset lineage runs."""
    records = [{"entity_id": "e-99", "timestamp": 500.0, "payload": "data"}]
    res = orchestrator.run_governance_pipeline("multi_input_job", records)
    assert res["status"] == "GOVERNANCE_PASSED"
    assert res["quality_score_pct"] == 100.0
