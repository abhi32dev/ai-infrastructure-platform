"""
Swarm Orchestrator: Runs 4-Agent Pipeline for Automated Test Matrix Generation.
"""
from .agents import (
    MicroserviceSpec,
    SpecAnalystAgent,
    PytestSynthesisAgent,
    SecurityChaosAgent,
    QualityGatekeeperAgent,
    SwarmReport
)

class SRESwarmOrchestrator:
    """
    Coordinates collaborative multi-agent execution pipeline.
    """
    def __init__(self):
        self.analyst = SpecAnalystAgent()
        self.synthesizer = PytestSynthesisAgent()
        self.security = SecurityChaosAgent()
        self.gatekeeper = QualityGatekeeperAgent()

    def process_spec(self, spec: MicroserviceSpec) -> SwarmReport:
        # Step 1: Spec Analysis
        analyst_msg = self.analyst.analyze(spec)

        # Step 2: Test Code Generation
        synth_msg = self.synthesizer.synthesize(spec, analyst_msg)

        # Step 3: Security & Chaos Audit
        sec_msg = self.security.audit_security(spec)

        # Step 4: Quality Gatekeeper Certification
        logs = [analyst_msg, synth_msg, sec_msg]
        report = self.gatekeeper.certify(spec, logs, synth_msg.generated_code or "")
        return report
