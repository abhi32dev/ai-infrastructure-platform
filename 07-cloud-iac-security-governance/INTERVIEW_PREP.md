# 🎤 Staff / Principal AI Infrastructure & Cloud Security Interview Guide

This guide bridges the code in **Project 7 (`07-cloud-iac-security-governance`)** directly to Staff/Principal-level questions asked by FAANG, Tier-1 AI startups, and top product companies.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you enforce multi-environment Infrastructure-as-Code consistency without environment drift?"
> **Staff Engineer Answer**:
> "In `07-cloud-iac-security-governance`, we defined a standardized Python **AWS CDK Golden Path Template** ([`src/cdk_golden_path.py`](src/cdk_golden_path.py)).
> 
> The CDK stack generator accepts target environment parameters (`Dev`, `QA`, `Stage`, `Prod`) and synthesizes account-ID-aware stack definitions. It automatically provisions standardized tiered VPC subnets, Application Load Balancers, ECS task roles, and CloudWatch log groups. This eliminates manual configuration drift across all 4 environments."

---

### Q2: "How do you audit IAM policies to prevent over-permissioning across platform service roles?"
> **Staff Engineer Answer**:
> "We implement automated **Least-Privilege Static Policy Auditing** in CI/CD ([`src/iam_policy_validator.py`](src/iam_policy_validator.py)).
> 
> Before any IAM role or CDK deployment is synthesized, our static analyzer inspects policy statements for:
> 1. **Wildcard Action Violations**: Flagging broad `*` actions (e.g. `s3:*` or `dynamodb:*`).
> 2. **Wildcard Resource Violations**: Enforcing specific resource ARNs (e.g. `arn:aws:s3:::bucket/*`).
> 3. **Production MFA Gates**: Verifying `aws:MultiFactorAuthPresent` conditions on sensitive production roles.
> 
> If a PR contains an over-permissioned statement, the CI security gate rejects the merge."

---

### Q3: "How do you manage endpoint security across heterogeneous EC2 instance fleets?"
> **Staff Engineer Answer**:
> "Security is not limited to cloud IAM. We owned end-to-end endpoint security for the Amazon EC2 fleet ([`src/security_agent_lifecycle.py`](src/security_agent_lifecycle.py)).
> 
> We ran continuous compliance monitoring for 3 core host security agents:
> 1. **CrowdStrike Falcon**: Endpoint detection and response.
> 2. **Qualys**: Continuous vulnerability scanning.
> 3. **OPENS**: Host intrusion protection and compliance.
> 
> Our automated security daemon samples host health, verifies agent patch cadence across Amazon Linux 2 and Amazon Linux 2023 instances, and surfaces non-compliant hosts before they expose vulnerabilities."

---

## 🧪 Quick Test Checklist for Candidates
Run these commands in your workspace to test and demonstrate:
- `python3 demo_runner.py`: Executes all 4 cloud security and governance scenarios live.
- `pytest tests/`: Verifies unit and integration test suite.
- `python3 app.py`: Opens Cloud Security Dashboard at `http://127.0.0.1:8006` to synthesize CDK stacks and audit IAM policies.
