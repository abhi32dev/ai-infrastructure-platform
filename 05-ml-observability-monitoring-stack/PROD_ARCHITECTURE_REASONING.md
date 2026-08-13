# Production Architecture & Design Trade-offs: ML Observability Monitoring Stack

## 1. Executive Context & Business Motivation
Machine learning models deployed in production silently degrade over time due to data drift (distribution shifts in input features) and concept drift (shifts in relationship between features and target labels). Without statistical observability, silent model degradation causes bad automated decisions without raising traditional software exceptions.

This stack implements **Real-time Feature Drift Detection (Evidently AI) with Prometheus Metrics & Grafana Alerting**.

---

## 2. Technical Decisions & Architectural Trade-Offs

### A. Non-Parametric Kolmogorov-Smirnov (KS) Test vs PSI / Wasserstein Distance
- **Chosen Option**: **Kolmogorov-Smirnov (KS) Statistical Drift Test**.
- **Alternative Evaluated**: Population Stability Index (PSI).
- **Trade-Off Rationale**:
  - *PSI*: Requires continuous feature binning choices, sensitive to zero-count bins.
  - *KS-Test*: Non-parametric test operating on cumulative empirical distributions. Computes exact p-values ($p < 0.05$ indicates statistically significant drift) without requiring manual histogram binning.

### B. Prometheus Metric Exporter vs External Logging APIs
- **Chosen Option**: **Prometheus Counter / Gauge Metrics Exporter**.
- **Trade-Off Rationale**: Enables real-time scrape-based monitoring integrated directly into existing DevOps Grafana dashboards and Alertmanager notification channels.

---

## 3. Best Practices & Production Design Principles

1. **Alert Deduplication & Cooldown Windows**:
   - Suppresses repeated drift alerts within a 1-hour cooldown window to prevent alert fatigue.
2. **Zero-Variance & Constant Feature Guard**:
   - Handles constant numerical features (e.g. all values = 0.0) without throwing divide-by-zero or numerical precision warnings.
3. **P95 / P99 Latency Histogram Metrics**:
   - Measures inference latency distributions alongside data quality metrics.

---

## 4. Production Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Alert Fatigue from Noise** | Engineers ignore real drift | Kolmogorov-Smirnov $p < 0.05$ threshold + 1-hour alert cooldown. |
| **Zero-Variance Feature Inputs** | Math domain error in stats | Guard check returns $p=1.0$ (no drift) for constant arrays. |
| **Missing Reference Baseline** | Drift check cannot run | Default fallback baseline populated during model deployment initialization. |
