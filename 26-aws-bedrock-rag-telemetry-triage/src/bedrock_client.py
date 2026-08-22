"""
AWS Bedrock Runtime Client & LangChain RAG Triage Engine.
Supports Anthropic Claude 3.5 Sonnet / Haiku via Boto3 with deterministic offline fallback.
"""
import os
import json
from typing import Optional
from .models import TelemetryTrapPayload, TriageDiagnosis, RunbookDoc
from .vector_store import PGVectorRunbookStore

class BedrockTriageEngine:
    """
    RAG-driven Telemetry Triage utilizing AWS Bedrock and PGVector.
    """
    def __init__(self, region_name: str = "us-east-1", model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"):
        self.region_name = region_name
        self.model_id = model_id
        self.vector_store = PGVectorRunbookStore()
        self.has_real_bedrock = False

        # Attempt to initialize real boto3 bedrock-runtime client if credentials exist
        try:
            import boto3
            if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
                self.client = boto3.client("bedrock-runtime", region_name=self.region_name)
                self.has_real_bedrock = True
        except Exception:
            self.has_real_bedrock = False

    def triage_alarm(self, trap: TelemetryTrapPayload) -> TriageDiagnosis:
        """
        Executes RAG Pipeline:
        1. Query PGVector for top matching historical runbooks.
        2. Format prompt context.
        3. Call AWS Bedrock Claude 3.5 Sonnet for structured diagnosis.
        """
        # 1. RAG Retrieval from PGVector
        query_context = f"{trap.vendor.value} {trap.oid} {trap.raw_message}"
        matching_runbooks = self.vector_store.search_similar_runbooks(query_context, vendor=trap.vendor, top_k=1)
        best_runbook: Optional[RunbookDoc] = matching_runbooks[0] if matching_runbooks else None

        # 2. Invoke Bedrock or Deterministic High-Fidelity Synthesizer
        if self.has_real_bedrock:
            try:
                prompt = self._build_prompt(trap, best_runbook)
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "temperature": 0.0,
                    "messages": [{"role": "user", "content": prompt}]
                })
                response = self.client.invoke_model(modelId=self.model_id, body=body)
                resp_json = json.loads(response["body"].read().decode())
                llm_output = resp_json["content"][0]["text"]
                return self._parse_llm_json(llm_output, trap, best_runbook)
            except Exception:
                pass # Fall through to resilient deterministic synthesis

        # High-Fidelity Deterministic Fallback Synthesis (Guaranteed Zero Runtime Exceptions)
        root_cause = best_runbook.root_cause if best_runbook else f"Unclassified edge fault on OID {trap.oid}: {trap.raw_message}"
        remediation = best_runbook.remediation_steps[0] if best_runbook else "Escalate to Tier-2 SRE for log analysis."
        confidence = best_runbook.similarity_score if best_runbook else 0.65

        is_auto_eligible = trap.severity.value in ["MINOR", "WARNING"] and best_runbook is not None
        cmd = "cbrs-cli refresh-grant --force" if "SAS" in root_cause else None

        return TriageDiagnosis(
            event_id=trap.event_id,
            node_id=trap.node_id,
            predicted_root_cause=root_cause,
            confidence_score=confidence,
            matching_runbook_id=best_runbook.runbook_id if best_runbook else None,
            recommended_action=remediation,
            automated_remediation_eligible=is_auto_eligible,
            remediation_command=cmd,
            escalation_team="SRE-Edge-AutoRemediation" if is_auto_eligible else "SRE-Edge-Tier2"
        )

    def _build_prompt(self, trap: TelemetryTrapPayload, runbook: Optional[RunbookDoc]) -> str:
        rb_text = f"Runbook ID: {runbook.runbook_id}\nRoot Cause: {runbook.root_cause}\nSteps: {runbook.remediation_steps}" if runbook else "No direct runbook match."
        return f"""You are Comcast CONDOR AI SRE Assistant. Diagnose the following telemetry trap:
Event ID: {trap.event_id}
Node ID: {trap.node_id}
Vendor: {trap.vendor.value}
Severity: {trap.severity.value}
OID: {trap.oid}
Message: {trap.raw_message}

Reference Runbook Context:
{rb_text}

Output ONLY valid JSON matching this schema:
{{
  "predicted_root_cause": "...",
  "confidence_score": 0.95,
  "matching_runbook_id": "...",
  "recommended_action": "...",
  "automated_remediation_eligible": true,
  "remediation_command": "...",
  "escalation_team": "..."
}}"""

    def _parse_llm_json(self, text: str, trap: TelemetryTrapPayload, rb: Optional[RunbookDoc]) -> TriageDiagnosis:
        clean = text.strip()
        if clean.startswith("```json"):
            clean = clean[7:-3].strip()
        data = json.loads(clean)
        return TriageDiagnosis(
            event_id=trap.event_id,
            node_id=trap.node_id,
            predicted_root_cause=data.get("predicted_root_cause", "Diagnosed fault"),
            confidence_score=float(data.get("confidence_score", 0.90)),
            matching_runbook_id=data.get("matching_runbook_id", rb.runbook_id if rb else None),
            recommended_action=data.get("recommended_action", "Apply standard operating procedure."),
            automated_remediation_eligible=bool(data.get("automated_remediation_eligible", False)),
            remediation_command=data.get("remediation_command"),
            escalation_team=data.get("escalation_team", "SRE-Edge-Tier2")
        )
