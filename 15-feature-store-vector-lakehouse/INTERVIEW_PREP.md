# 🎤 Staff AI Platform Interview Guide: Feature Store & Vector Lakehouse

This guide bridges **Project 15 (`15-feature-store-vector-lakehouse`)** to Staff/Principal-level questions on online/offline feature serving and point-in-time joins.

---

## 💡 Key Architectural Concepts & Interview Answers

### Q1: "How do you prevent temporal data leakage during training set generation?"
> **Staff Engineer Answer**:
> "In `src/feature_lakehouse_engine.py`, we execute PyArrow ASOF joins where feature observation timestamps strictly precede the label event timestamp (`feature_time <= event_time`)."

### Q2: "How does the dual-layer feature store architecture balance latency and scale?"
> **Staff Engineer Answer**:
> "Online features are pre-materialized in Redis for sub-2ms real-time inference serving, while offline features reside in Parquet/Delta Lake tables for large-scale distributed model training."

### Q3: "How do you handle missing feature values during online inference?"
> **Staff Engineer Answer**:
> "We apply pre-calculated mean/median baseline imputation directly in the feature retrieval client to prevent model null exceptions."
