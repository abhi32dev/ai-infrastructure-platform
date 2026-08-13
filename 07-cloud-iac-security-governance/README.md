# 🛡️ Project 7: Multi-Account Cloud IaC & Security Governance Engine

> [!TIP]
> 🔀 **[CLICK HERE TO VIEW LIVE RENDERED FLOWCHART & CONTROL FLOW BLUEPRINT](https://abhi32dev.github.io/ai-infrastructure-platform/07-cloud-iac-security-governance/FLOWCHART.html)**
> 
> 📄 **[View Architecture Reasoning & Design Trade-offs](PROD_ARCHITECTURE_REASONING.md)** | 🌐 **[Main Platform Showcase](https://abhi32dev.github.io/ai-infrastructure-platform/)**


![2D Control Flow Diagram](FLOWCHART.svg)

---

A production-grade **Cloud Infrastructure & Security Governance Engine** implementing AWS CDK golden path stack synthesis across 4 environments (Dev, QA, Stage, Prod), tiered VPC subnet isolation, static IAM policy security auditing for least privilege, and EC2 endpoint security agent compliance tracking (CrowdStrike, Qualys, OPENS).

---

## 🎯 System Capabilities

- **AWS CDK Golden Path Generator**: Synthesizes environment-aware CDK stacks with standardized VPC subnet tiers and IAM roles.
- **Least-Privilege IAM Policy Validator**: Static analysis engine flagging over-permissioned wildcard statements (`*`) and enforcing MFA gates.
- **EC2 Security Agent Lifecycle Monitor**: Fleet compliance tracker for CrowdStrike Falcon, Qualys vulnerability scanner, and OPENS HIPS agents.

---

## 📁 Repository Structure

```text
07-cloud-iac-security-governance/
├── src/
│   ├── cdk_golden_path.py           # Multi-account AWS CDK stack generator
│   ├── iam_policy_validator.py       # Least-privilege IAM policy static audit engine
│   ├── security_agent_lifecycle.py   # EC2 endpoint security agent compliance tracker
│   └── cloud_security_governance.py # Master Cloud IaC & Security Platform Orchestrator
├── tests/
│   └── test_cloud_governance.py     # Pytest test suite for CDK, IAM, and security monitoring
├── app.py                            # FastAPI REST server & embedded Security Dashboard
├── demo_runner.py                    # Interactive CLI script running 4 cloud security scenarios
├── requirements.txt                  # Project dependencies
├── README.md                         # System documentation
└── INTERVIEW_PREP.md                 # Staff AI Infra & Cloud Security Interview Guide
```

---

## 🚦 Quick Start & Interactive Demo

```bash
python3 demo_runner.py  # Runs CLI demo
pytest tests/           # Runs test suite
python3 app.py          # Launches Cloud Security Dashboard at http://127.0.0.1:8006
```