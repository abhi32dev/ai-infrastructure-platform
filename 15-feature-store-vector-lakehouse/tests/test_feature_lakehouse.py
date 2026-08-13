"""
Expanded Test Suite for Project 15 - Feature Store & Vector Lakehouse (Feast, Apache Iceberg & PyArrow).
Includes production edge cases for zero-row scans, missing entities, duplicate feature overrides, and high-dimensional column pruning.
"""

import time
import pytest
from src.feature_store import MLFeatureStore
from src.arrow_lakehouse import PyArrowVectorLakehouse
from src.lakehouse_orchestrator import FeatureLakehouseOrchestrator


@pytest.fixture
def feature_store():
    return MLFeatureStore()


@pytest.fixture
def lakehouse():
    return PyArrowVectorLakehouse()


@pytest.fixture
def orchestrator():
    return FeatureLakehouseOrchestrator()


def test_01_push_and_get_online_feature(feature_store):
    """Test 1: Verifies pushing features to Online Store and low-latency retrieval (< 2ms)."""
    feature_store.push_online_feature("user-101", "click_rate_7d", 0.145)
    res = feature_store.get_online_features("user-101", ["click_rate_7d"])
    assert res["found"] is True
    assert res["features"]["click_rate_7d"] == 0.145
    assert res["latency_ms"] < 2.0


def test_02_online_feature_missing_entity(feature_store):
    """Test 2: Verifies feature store handling non-existent entity gracefully."""
    res = feature_store.get_online_features("user-missing", ["click_rate_7d"])
    assert res["found"] is False
    assert res["features"] == {}


def test_03_time_travel_feature_extraction(feature_store):
    """Test 3: Verifies point-in-time feature extraction for training datasets."""
    t_start = time.time()
    feature_store.push_online_feature("user-202", "churn_risk_score", 0.82)
    
    extracted = feature_store.time_travel_join(["user-202"], as_of_timestamp=t_start + 10.0)
    assert len(extracted) == 1
    assert extracted[0]["churn_risk_score"] == 0.82


def test_04_pyarrow_zero_copy_columnar_query(lakehouse):
    """Test 4: Verifies Apache Iceberg / PyArrow zero-copy column pruning scan."""
    res = lakehouse.query_columnar_vectors(columns=["embedding_v1", "embedding_v2"], max_rows=1000)
    assert res.rows_scanned == 1000
    assert res.zero_copy_bytes == 1000 * 2 * 64
    assert res.scan_latency_ms < 5.0


def test_05_orchestrator_feature_pipeline(orchestrator):
    """Test 5: Verifies master Feature Lakehouse orchestrator pipeline execution."""
    res = orchestrator.process_feature_pipeline("entity-99", {"feat_a": 1.2, "feat_b": 3.4})
    assert res["status"] == "PIPELINE_COMPLETED"
    assert res["online_features"]["feat_a"] == 1.2
    assert res["lakehouse_rows_scanned"] == 5000


def test_06_online_feature_update_overwrite(feature_store):
    """Test 6: Verifies updating existing feature values in Online Store."""
    feature_store.push_online_feature("user-303", "score", 10.0)
    feature_store.push_online_feature("user-303", "score", 25.0)  # Overwrite!
    res = feature_store.get_online_features("user-303", ["score"])
    assert res["features"]["score"] == 25.0


def test_07_multiple_feature_retrieval(feature_store):
    """Test 7: Verifies retrieving multi-feature vectors in a single request."""
    feature_store.push_online_feature("user-404", "f1", 1.0)
    feature_store.push_online_feature("user-404", "f2", 2.0)
    res = feature_store.get_online_features("user-404", ["f1", "f2", "f3_missing"])
    assert res["features"]["f1"] == 1.0
    assert res["features"]["f2"] == 2.0
    assert res["features"]["f3_missing"] == 0.0  # Default fallback


def test_08_lakehouse_empty_columns(lakehouse):
    """Test 8: Verifies PyArrow lakehouse handling zero-column scans."""
    res = lakehouse.query_columnar_vectors(columns=[], max_rows=500)
    assert res.zero_copy_bytes == 0


def test_09_time_travel_future_timestamp_filtering(feature_store):
    """Test 9 [Production Edge Case]: Verifies time travel join ignoring features published after as_of timestamp."""
    t_past = time.time() - 100.0
    feature_store.push_online_feature("user-future", "future_feat", 99.0)  # Current timestamp > t_past
    extracted = feature_store.time_travel_join(["user-future"], as_of_timestamp=t_past)
    assert len(extracted) == 0  # No features existed as of t_past!


def test_10_lakehouse_high_dimensional_vector_scan(lakehouse):
    """Test 10 [Production Edge Case]: Verifies PyArrow zero-copy scanning over 1,024 dimensional embedding tables."""
    res = lakehouse.query_columnar_vectors(columns=[f"dim_{i}" for i in range(1024)], max_rows=5000)
    assert res.rows_scanned == 5000
    assert res.zero_copy_bytes == 5000 * 1024 * 64


def test_11_store_negative_feature_values(feature_store):
    """Test 11 [Production Edge Case]: Verifies storing and serving negative floating point feature values."""
    feature_store.push_online_feature("entity-neg", "z_score", -2.85)
    res = feature_store.get_online_features("entity-neg", ["z_score"])
    assert res["features"]["z_score"] == -2.85


def test_12_orchestrator_empty_feature_map(orchestrator):
    """Test 12 [Production Edge Case]: Verifies feature orchestrator handling empty feature dictionary cleanly."""
    res = orchestrator.process_feature_pipeline("entity-empty", {})
    assert res["status"] == "PIPELINE_COMPLETED"
    assert res["online_features"] == {}
