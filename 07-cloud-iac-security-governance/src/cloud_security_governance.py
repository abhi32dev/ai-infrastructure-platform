"""
Master Cloud IaC & Security Governance Orchestrator.
Integrates Multi-Account CDK Stack Synthesis, Least-Privilege IAM Policy Static Auditing,
and EC2 Endpoint Security Agent Compliance Monitoring.
"""

from typing import Any, Dict, List
from src.cdk_golden_path import CDKGoldenPathGenerator, CDKGoldenPathStack
from src.iam_policy_validator import IAMPolicyValidator, IAMSecurityViolation
from src.security_agent_lifecycle import HostSecurityStatus, SecurityAgentLifecycleManager


class CloudSecurityGovernanceOrchestrator:
    def __init__(self):
        print("[CLOUD GOVERNANCE] Initializing Cloud IaC & Security Governance Engine...")
        self.cdk = CDKGoldenPathGenerator()
        self.iam_validator = IAMPolicyValidator()
        self.security_manager = SecurityAgentLifecycleManager()

    def synthesize_cdk_stack(self, environment: str) -> CDKGoldenPathStack:
        """Synthesizes environment CDK stack definition."""
        return self.cdk.generate_environment_stack(environment)

    def audit_iam_policy(self, policy_name: str, policy_doc: Dict[str, Any], is_prod: bool = False) -> List[IAMSecurityViolation]:
        """Audits IAM policy for least-privilege security violations."""
        return self.iam_validator.validate_policy(policy_name, policy_doc, is_production=is_prod)

    def audit_ec2_host_security(self, instance_id: str, os_ver: str, agents: Dict[str, str]) -> HostSecurityStatus:
        """Audits EC2 endpoint security agent compliance."""
        return self.security_manager.audit_host_security(instance_id, os_ver, agents)
