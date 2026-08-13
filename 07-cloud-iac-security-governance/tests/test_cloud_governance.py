"""
Expanded Test Suite for Project 7 - Cloud IaC, Security & Governance.
Tests Multi-Account AWS CDK Golden Path synthesis, VPC Tiered Subnet Isolation, Static IAM Policy Audit Engine,
Least-Privilege violations, and EC2 Endpoint Security Agent Compliance tracking.
"""

import pytest
from src.cdk_golden_path import CDKGoldenPathGenerator
from src.iam_policy_validator import IAMPolicyValidator
from src.security_agent_lifecycle import SecurityAgentLifecycleManager, AgentHealthStatus


@pytest.fixture
def cdk_gen():
    return CDKGoldenPathGenerator()


@pytest.fixture
def iam_validator():
    return IAMPolicyValidator()


@pytest.fixture
def sec_manager():
    return SecurityAgentLifecycleManager()


def test_01_cdk_vpc_subnet_isolation(cdk_gen):
    """Test 1: Verifies AWS CDK Tiered VPC Subnet Isolation (Public, Private, Protected)."""
    stack = cdk_gen.generate_environment_stack(environment="Prod")
    subnets = stack.vpc_subnet_tiers
    assert len(subnets) == 3
    names = [s.tier_name for s in subnets]
    assert "Public-ALB-Tier" in names
    assert "Private-App-Tier" in names
    assert "Protected-Data-Tier" in names


def test_02_cdk_multi_account_golden_path(cdk_gen):
    """Test 2: Verifies AWS CDK Golden Path Stack synthesis across Dev, QA, Stage, and Prod."""
    dev_stack = cdk_gen.generate_environment_stack("Dev")
    prod_stack = cdk_gen.generate_environment_stack("Prod")
    assert dev_stack.environment == "Dev"
    assert prod_stack.environment == "Prod"
    assert dev_stack.account_id != prod_stack.account_id


def test_03_iam_policy_wildcard_permission_violation(iam_validator):
    """Test 3: Verifies IAM policy audit engine detecting dangerous wildcard permissions (Action: "*")."""
    bad_policy = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]
    }
    violations = iam_validator.validate_policy("WildcardPolicy", bad_policy, is_production=True)
    assert len(violations) >= 2
    types = [v.violation_type for v in violations]
    assert "WILDCARD_ACTION" in types
    assert "WILDCARD_RESOURCE" in types


def test_04_iam_policy_least_privilege_audit(iam_validator):
    """Test 4: Verifies least-privilege policy validation passing for tightly scoped ARNs."""
    good_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:PutObject"],
            "Resource": ["arn:aws:s3:::condor-bucket/*"],
            "Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}}
        }]
    }
    violations = iam_validator.validate_policy("GoodPolicy", good_policy, is_production=True)
    assert len(violations) == 0


def test_05_security_agent_status_tracking(sec_manager):
    """Test 5: Verifies EC2 security monitoring agent status tracking (CrowdStrike, Qualys)."""
    status = sec_manager.audit_host_security(
        instance_id="i-108",
        os_version="Amazon Linux 2023",
        installed_agents={"crowdstrike": "7.10.0", "qualys": "3.1.5", "opens": "2.4.1"}
    )
    assert status.instance_id == "i-108"
    assert status.crowdstrike_agent_status == AgentHealthStatus.COMPLIANT_ACTIVE
    assert status.overall_compliant is True


def test_06_unregistered_security_agent_alert(sec_manager):
    """Test 6: Verifies alert generation when an endpoint misses required agent software."""
    status = sec_manager.audit_host_security(
        instance_id="i-missing-qualys",
        os_version="Amazon Linux 2",
        installed_agents={"crowdstrike": "7.10.0"}  # Missing qualys and opens!
    )
    assert status.overall_compliant is False
    assert status.qualys_scanner_status == AgentHealthStatus.NON_COMPLIANT


def test_07_invalid_json_iam_policy_handling(iam_validator):
    """Test 7: Verifies IAM policy auditor handling empty policies safely."""
    violations = iam_validator.validate_policy("EmptyPolicy", {}, is_production=False)
    assert len(violations) == 0


def test_08_security_agent_outdated_patch_pending(sec_manager):
    """Test 8: Verifies patch pending status when agent version is outdated."""
    status = sec_manager.audit_host_security(
        instance_id="i-outdated",
        os_version="Amazon Linux 2023",
        installed_agents={"crowdstrike": "6.0.0", "qualys": "3.1.5", "opens": "2.4.1"}
    )
    assert status.crowdstrike_agent_status == AgentHealthStatus.PATCH_PENDING
    assert status.overall_compliant is False


def test_09_cdk_unrecognized_environment(cdk_gen):
    """Test 9 [Production Edge Case]: Verifies CDK generator handling custom/unknown environment name gracefully."""
    stack = cdk_gen.generate_environment_stack("CustomStaging")
    assert stack.environment == "CustomStaging"
    assert len(stack.vpc_subnet_tiers) == 3


def test_10_iam_policy_missing_statement_key(iam_validator):
    """Test 10 [Production Edge Case]: Verifies IAM validator handling policy dict missing 'Statement' key."""
    malformed_policy = {"Version": "2012-10-17"}
    violations = iam_validator.validate_policy("MalformedPolicy", malformed_policy, is_production=True)
    assert len(violations) == 0


def test_11_security_agent_zero_agents_installed(sec_manager):
    """Test 11 [Production Edge Case]: Verifies security agent manager flagging instance with 0 agents installed."""
    status = sec_manager.audit_host_security("i-bare-metal", "Ubuntu 22.04", {})
    assert status.overall_compliant is False
    assert status.crowdstrike_agent_status == AgentHealthStatus.NON_COMPLIANT


def test_12_iam_policy_non_prod_permissive_warning(iam_validator):
    """Test 12 [Production Edge Case]: Verifies IAM validator emitting non-blocking warnings in Dev environments."""
    dev_wildcard = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "s3:*", "Resource": "*"}]}
    violations = iam_validator.validate_policy("DevWildcard", dev_wildcard, is_production=False)
    assert len(violations) >= 1

