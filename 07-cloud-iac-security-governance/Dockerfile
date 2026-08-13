# Production Dockerfile for Project 7 - Cloud IaC & Security Governance
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    node_js \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8006

ENV PYTHONPATH=/app
ENV PORT=8006

CMD ["python3", "app.py"]
