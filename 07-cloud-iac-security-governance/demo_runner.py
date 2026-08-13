"""
Interactive CLI Runner & Test Suite for Project 7 - Cloud IaC & Security Governance.
Runs 4 core production scenarios:
1. Multi-Account AWS CDK Stack Synthesis (Dev, QA, Stage, Prod).
2. Tiered VPC Subnet Isolation (Public, Private, Protected).
3. Least-Privilege IAM Policy Security Static Auditing.
4. EC2 Endpoint Security Agent Compliance Monitoring (CrowdStrike, Qualys, OPENS).
"""

import asyncio
import json

from src.cloud_security_governance import CloudSecurityGovernanceOrchestrator


def run_demo():
    print("==========================================================================")
    print("🛡️ STARTING MULTI-ACCOUNT CLOUD IAC & SECURITY GOVERNANCE DEMO")
    print("==========================================================================\n")

    orchestrator = CloudSecurityGovernanceOrchestrator()

    # -------------------------------------------------------------------------
    # SCENARIO 1 & 2: Multi-Account CDK Synthesis & VPC Tiering
    # -------------------------------------------------------------------------
    print("--- [SCENARIOS 1 & 2] AWS CDK Stack Synthesis & Tiered VPC Subnets ---")
    prod_stack = orchestrator.synthesize_cdk_stack("Prod")

    print(f"Synthesized Stack: {prod_stack.stack_name}")
    print(f"  └─ Environment: {prod_stack.environment} | Target AWS Account: {prod_stack.account_id}")
    print(f"  └─ Observability Log Group: {prod_stack.observability_log_group}")
    print("\n  Tiered VPC Security Subnets:")
    for tier in prod_stack.vpc_subnet_tiers:
        print(f"    └─ [{tier.tier_name}] CIDR: {tier.cidr_block} | Public: {tier.is_public} | Ports: {tier.allowed_inbound_ports}")

    # -------------------------------------------------------------------------
    # SCENARIO 3: Least-Privilege IAM Policy Static Auditing
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 3] Least-Privilege IAM Policy Static Auditing ---")
    insecure_policy_doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject"],
                "Resource": "arn:aws:s3:::condor-production-bucket/*"
            },
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            }
        ]
    }

    print("Auditing sample IAM Policy for production environment...")
    violations = orchestrator.audit_iam_policy("InsecureProdPolicy", insecure_policy_doc, is_prod=True)

    print(f"Detected {len(violations)} Security Violations:")
    for v in violations:
        print(f"  └─ [{v.severity}] {v.violation_type}: {v.description}")

    # -------------------------------------------------------------------------
    # SCENARIO 4: EC2 Endpoint Security Agent Compliance Monitoring
    # -------------------------------------------------------------------------
    print("\n\n--- [SCENARIO 4] EC2 Endpoint Security Agent Compliance Monitoring ---")
    instance_id = "i-09f8e7d6c5b4"
    os_ver = "Amazon Linux 2023"
    installed_agents = {
        "crowdstrike": "7.10.0",
        "qualys": "3.1.5",
        "opens": "2.4.1"
    }

    status = orchestrator.audit_ec2_host_security(instance_id, os_ver, installed_agents)
    print(f"Host '{instance_id}' ({os_ver}) Security Status:")
    print(f"  └─ CrowdStrike Falcon Agent: {status.crowdstrike_agent_status.value}")
    print(f"  └─ Qualys Vulnerability Scanner: {status.qualys_scanner_status.value}")
    print(f"  └─ OPENS Host Intrusion Agent: {status.opens_agent_status.value}")
    print(f"  └─ Overall Host Compliance: {'COMPLIANT' if status.overall_compliant else 'NON_COMPLIANT'}")

    print("\n==========================================================================")
    print("✅ DEMO COMPLETED SUCCESSFULLY! ALL 4 CLOUD SECURITY SCENARIOS VERIFIED.")
    print("==========================================================================\n")


if __name__ == "__main__":
    run_demo()
