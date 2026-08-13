# AWS Infrastructure Cost Governance: ALB Target Routing vs API Gateway

## 1. Architectural Cost Analysis
When architecting high-volume microservices handling > 100 million API requests per day:
- **AWS API Gateway**: Charges $3.50 per million requests plus data transfer fees. At 100M requests/day, API Gateway costs $350/day ($10,500/month) purely for routing overhead.
- **AWS Application Load Balancer (ALB)**: Charges $0.0225 per LCU-hour. An ALB handling 100M requests/day costs approximately $18/day ($540/month).

## 2. Recommendation
For sustained, high-throughput microservices (such as edge telemetry and LLM token proxy endpoints), route traffic directly through **AWS Application Load Balancers with host/path-based target rules**, reducing monthly network routing infrastructure costs by 94.8%.
