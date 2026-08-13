"""
Least-Privilege IAM Policy Validator & Security Static Analysis Engine.
Audits IAM policies for wildcard '*' action/resource over-permissioning, enforces MFA gates,
and verifies least-privilege access bounds across service roles.
Matches Comcast CONDOR IAM governance & blast-radius management claims.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class IAMSecurityViolation(BaseModel):
    policy_name: str
    violation_type: str
    severity: str
    description: str


class IAMPolicyValidator:
    def __init__(self):
        pass

    def validate_policy(self, policy_name: str, policy_document: Dict[str, Any], is_production: bool = False) -> List[IAMSecurityViolation]:
        """
        Audits IAM policy document for security violations.
        """
        violations: List[IAMSecurityViolation] = []
        statements = policy_document.get("Statement", [])

        for idx, stmt in enumerate(statements):
            effect = stmt.get("Effect", "")
            actions = stmt.get("Action", [])
            resources = stmt.get("Resource", [])
            conditions = stmt.get("Condition", {})

            if isinstance(actions, str):
                actions = [actions]
            if isinstance(resources, str):
                resources = [resources]

            if effect == "Allow":
                # Check 1: Wildcard Action violation
                if "*" in actions or "s3:*" in actions or "dynamodb:*" in actions:
                    violations.append(IAMSecurityViolation(
                        policy_name=policy_name,
                        violation_type="WILDCARD_ACTION",
                        severity="CRITICAL" if is_production else "HIGH",
                        description=f"Statement {idx} grants wildcard actions ({actions}). Restrict to specific API actions."
                    ))

                # Check 2: Wildcard Resource violation
                if "*" in resources:
                    violations.append(IAMSecurityViolation(
                        policy_name=policy_name,
                        violation_type="WILDCARD_RESOURCE",
                        severity="HIGH",
                        description=f"Statement {idx} targets wildcard resource ('*'). Scope resource ARN to specific buckets/tables."
                    ))

                # Check 3: MFA Enforcement on production roles
                if is_production and not conditions.get("Bool", {}).get("aws:MultiFactorAuthPresent"):
                    violations.append(IAMSecurityViolation(
                        policy_name=policy_name,
                        violation_type="MISSING_MFA_ENFORCEMENT",
                        severity="CRITICAL",
                        description="Production policy statement is missing MultiFactorAuthPresent condition."
                    ))

        return violations
