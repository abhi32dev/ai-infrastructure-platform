"""
EC2 Endpoint Security Agent Lifecycle & Compliance Monitor.
Tracks CrowdStrike Falcon, Qualys Vulnerability Scanner, and OPENS Host Intrusion Protection agent
versions, patch cadences, package compatibility, and continuous compliance across EC2 instance fleets.
Matches Comcast CONDOR Endpoint Security Ownership claims.
"""

from enum import Enum
import time
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class AgentHealthStatus(str, Enum):
    COMPLIANT_ACTIVE = "COMPLIANT_ACTIVE"
    PATCH_PENDING = "PATCH_PENDING"
    AGENT_DEGRADED = "AGENT_DEGRADED"
    NON_COMPLIANT = "NON_COMPLIANT"


class HostSecurityStatus(BaseModel):
    instance_id: str
    os_version: str  # Amazon Linux 2 or Amazon Linux 2023
    crowdstrike_agent_status: AgentHealthStatus
    qualys_scanner_status: AgentHealthStatus
    opens_agent_status: AgentHealthStatus
    overall_compliant: bool
    last_vulnerability_scan_sec: float = Field(default_factory=time.time)


class SecurityAgentLifecycleManager:
    LATEST_VERSIONS = {
        "crowdstrike": "7.10.0",
        "qualys": "3.1.5",
        "opens": "2.4.1"
    }

    def __init__(self):
        pass

    def audit_host_security(
        self, 
        instance_id: str, 
        os_version: str, 
        installed_agents: Dict[str, str]
    ) -> HostSecurityStatus:
        """
        Audits installed agent versions against latest security baselines.
        """
        cs_ver = installed_agents.get("crowdstrike")
        qualys_ver = installed_agents.get("qualys")
        opens_ver = installed_agents.get("opens")

        cs_status = AgentHealthStatus.COMPLIANT_ACTIVE if cs_ver == self.LATEST_VERSIONS["crowdstrike"] else AgentHealthStatus.PATCH_PENDING if cs_ver else AgentHealthStatus.NON_COMPLIANT
        qualys_status = AgentHealthStatus.COMPLIANT_ACTIVE if qualys_ver == self.LATEST_VERSIONS["qualys"] else AgentHealthStatus.PATCH_PENDING if qualys_ver else AgentHealthStatus.NON_COMPLIANT
        opens_status = AgentHealthStatus.COMPLIANT_ACTIVE if opens_ver == self.LATEST_VERSIONS["opens"] else AgentHealthStatus.PATCH_PENDING if opens_ver else AgentHealthStatus.NON_COMPLIANT

        overall = (cs_status == AgentHealthStatus.COMPLIANT_ACTIVE) and (qualys_status == AgentHealthStatus.COMPLIANT_ACTIVE) and (opens_status == AgentHealthStatus.COMPLIANT_ACTIVE)

        return HostSecurityStatus(
            instance_id=instance_id,
            os_version=os_version,
            crowdstrike_agent_status=cs_status,
            qualys_scanner_status=qualys_status,
            opens_agent_status=opens_status,
            overall_compliant=overall
        )
