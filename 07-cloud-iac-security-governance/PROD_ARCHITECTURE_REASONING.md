# Production Architecture & Design Trade-offs: Cloud IaC Security Governance

## 1. Executive Context & Business Motivation
Misconfigured Cloud Infrastructure as Code (IaC) templates (e.g. AWS CDK, Terraform) are the leading cause of cloud security breaches. Overly permissive IAM policies (`"Action": "*"`), unencrypted S3 buckets, and exposed public endpoints compromise data compliance.

This framework implements an **Automated IaC Security Policy Validator & Host Security Lifecycle Engine**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Static AST Policy AST Validation vs Post-Deployment Auditing
- **Chosen Option**: **Pre-Deployment Static AST & Policy Rule Validation**.
- **Alternative Evaluated**: Post-deployment CloudTrail / Security Hub auditing.
- **Trade-Off Rationale**:
  - *Post-Deployment Auditing*: Catches vulnerabilities *after* resources are live in production, exposing data during the window prior to remediation.
  - *Pre-Deployment Validation*: Blocks dangerous IaC stacks during CI/CD build pipelines before cloud resources are provisioned.

### B. Rule-Based Regex vs OPA (Open Policy Agent) Rego
- **Chosen Option**: **Modular Python Policy Engine with OPA Compatibility**.
- **Trade-Off Rationale**: Allows programmatic inspection of CDK constructs and Terraform JSON plans with zero external binary dependencies during local testing.

---

## 3. Best Practices & Production Design Principles

1. **Principle of Least Privilege (PoLP)**:
   - Scans IAM policy statements for wildcard actions (`*`) and unrestricted resource scopes (`"Resource": "*"`).
2. **Mandatory Encryption & Public Access Block**:
   - Enforces default KMS key encryption on S3 buckets and EBS volumes.
3. **Automated CI/CD Quality Gates**:
   - Returns non-zero exit codes during git commit hooks and build pipelines if security severity is `HIGH` or `CRITICAL`.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Wildcard IAM Deployment** | Privilege escalation vulnerability | Pre-commit static AST scan blocks build pipeline. |
| **Unencrypted Cloud Storage** | Compliance violation (GDPR/HIPAA) | Automated rule enforcement checking `kms_key_id` presence. |
| **Bypassed CI/CD Gates** | Security regression in prod | Mandatory GitHub Branch Protection enforcing status check pass. |
