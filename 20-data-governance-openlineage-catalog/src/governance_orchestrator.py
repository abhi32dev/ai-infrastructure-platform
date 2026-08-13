"""
Master Data Governance & OpenLineage Catalog Orchestrator.
Integrates OpenLineage Event Emitters, Marquez Lineage Graph Tracking, and Data Quality Contract Validation.
"""

from typing import Any, Dict, List
from src.openlineage_emitter import OpenLineageEmitter, OpenLineageEvent
from src.marquez_lineage import DatasetLineageGraph, MarquezLineageTracker
from src.data_contract_validator import DataContractValidationResult, DataContractValidator


class DataGovernanceOrchestrator:
    def __init__(self):
        self.emitter = OpenLineageEmitter()
        self.lineage_tracker = MarquezLineageTracker()
        self.contract_validator = DataContractValidator()

    def run_governance_pipeline(self, job_name: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs Data Contract Validation -> OpenLineage Emission -> Lineage Graph Recording."""
        # 1. Validate Data Quality Contract
        contract_res = self.contract_validator.validate_dataset_batch(records)
        if not contract_res.is_valid:
            return {
                "status": "DATA_CONTRACT_VIOLATION",
                "quality_score_pct": contract_res.quality_score_pct,
                "violations": contract_res.contract_violations
            }

        # 2. Emit OpenLineage Event
        run_id = f"run-{job_name}-001"
        inputs = ["raw_snmp_events"]
        outputs = ["curated_feature_store"]
        
        event = self.emitter.emit_job_event("COMPLETE", job_name, run_id, inputs, outputs)
        self.lineage_tracker.record_job_lineage(job_name, inputs, outputs)
        graph = self.lineage_tracker.export_graph_summary()

        return {
            "status": "GOVERNANCE_PASSED",
            "job_name": job_name,
            "run_id": run_id,
            "openlineage_event_type": event.event_type,
            "lineage_edges": graph.lineage_edges,
            "quality_score_pct": contract_res.quality_score_pct
        }
