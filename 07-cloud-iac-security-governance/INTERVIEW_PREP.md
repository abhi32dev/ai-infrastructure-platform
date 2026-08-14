# 🎤 Staff AI Platform Interview Guide: Cloud IaC Security Governance & AST Analysis

This guide bridges **Project 7 (`07-cloud-iac-security-governance`)** to Staff/Principal-level questions on automated cloud infrastructure security.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you prevent overly permissive IAM policies in CI/CD before infrastructure deployment?"
> **Staff Engineer Answer**:
> "In `src/cloud_governance.py`, we parse synthesized AWS CDK and CloudFormation Abstract Syntax Trees (AST). Any IAM policy containing wildcard actions (`Action: '*'`) or wildcard principals triggers a critical security build failure."

### Q2: "How do you enforce mandatory customer-managed encryption (KMS) on all cloud storage buckets?"
> **Staff Engineer Answer**:
> "The AST evaluator inspects S3 bucket property nodes. If `ServerSideEncryptionConfiguration` is missing or uses default keys, CDK Aspects inject customer-managed KMS key policies automatically."

### Q3: "How are infrastructure compliance findings exported for enterprise SOC auditing?"
> **Staff Engineer Answer**:
> "Violations are exported in standardized SARIF (Static Analysis Results Interchange Format) JSON format, integrating with GitHub Advanced Security and Datadog Compliance monitors."
