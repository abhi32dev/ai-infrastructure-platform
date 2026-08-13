"""
AWS CDK Multi-Account Infrastructure-as-Code (IaC) Stack Generator.
Defines account-ID-aware stack logic, tiered VPC subnet layouts (Public, Private, Protected),
and standardized golden path deployment templates across 4 AWS environments (Dev, QA, Stage, Prod).
Matches AWS CDK, CloudFormation, and Tiered VPC claims from Comcast CONDOR platform.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class VPCSubnetTier(BaseModel):
    tier_name: str
    cidr_block: str
    is_public: bool
    allowed_inbound_ports: List[int]


class CDKGoldenPathStack(BaseModel):
    stack_name: str
    environment: str
    account_id: str
    region: str
    vpc_subnet_tiers: List[VPCSubnetTier]
    least_privilege_iam_roles: List[str]
    observability_log_group: str
    drift_prevention_enabled: bool = True


class CDKGoldenPathGenerator:
    ACCOUNT_MAP = {
        "Dev": "111122223333",
        "QA": "444455556666",
        "Stage": "777788889999",
        "Prod": "999900001111"
    }

    def __init__(self, region: str = "us-west-2"):
        self.region = region

    def generate_environment_stack(self, environment: str) -> CDKGoldenPathStack:
        """
        Synthesizes a standardized, account-aware AWS CDK stack definition for target environment.
        """
        account_id = self.ACCOUNT_MAP.get(environment, "111122223333")
        stack_name = f"CONDOR-Platform-{environment}-Stack"

        # Tiered VPC Subnet Security Architecture
        subnet_tiers = [
            VPCSubnetTier(tier_name="Public-ALB-Tier", cidr_block="10.0.1.0/24", is_public=True, allowed_inbound_ports=[80, 443]),
            VPCSubnetTier(tier_name="Private-App-Tier", cidr_block="10.0.10.0/24", is_public=False, allowed_inbound_ports=[8000, 8080]),
            VPCSubnetTier(tier_name="Protected-Data-Tier", cidr_block="10.0.20.0/24", is_public=False, allowed_inbound_ports=[5432, 3306])
        ]

        roles = [
            f"arn:aws:iam::{account_id}:role/CONDOR-EC2-IngestionRole-{environment}",
            f"arn:aws:iam::{account_id}:role/CONDOR-LambdaWorkerRole-{environment}"
        ]

        log_group = f"/aws/condor/platform/{environment}/application-logs"

        return CDKGoldenPathStack(
            stack_name=stack_name,
            environment=environment,
            account_id=account_id,
            region=self.region,
            vpc_subnet_tiers=subnet_tiers,
            least_privilege_iam_roles=roles,
            observability_log_group=log_group
        )
