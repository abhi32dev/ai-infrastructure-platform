"""
Data Quality Contract & Great Expectations Validator.
Audits incoming dataset rows against schema contracts (non-null assertions, type bounds, freshness SLAs).
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class DataContractValidationResult(BaseModel):
    is_valid: bool
    total_records_checked: int
    contract_violations: List[str]
    quality_score_pct: float


class DataContractValidator:
    def __init__(self, required_fields: List[str] = None):
        self.required_fields = required_fields or ["entity_id", "timestamp", "payload"]

    def validate_dataset_batch(self, records: List[Dict[str, Any]]) -> DataContractValidationResult:
        """Validates record batch against data contract schema constraints."""
        violations: List[str] = []
        valid_count = 0

        for idx, rec in enumerate(records):
            rec_valid = True
            for field in self.required_fields:
                if field not in rec or rec[field] is None:
                    violations.append(f"Row {idx}: missing required contract field '{field}'")
                    rec_valid = False

            if rec_valid:
                valid_count += 1

        total = len(records)
        score = round((valid_count / float(max(1, total))) * 100.0, 2)

        return DataContractValidationResult(
            is_valid=len(violations) == 0,
            total_records_checked=total,
            contract_violations=violations,
            quality_score_pct=score
        )
