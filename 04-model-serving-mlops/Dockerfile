# Production Dockerfile for Project 4 - Model Serving & MLOps
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8003

ENV PYTHONPATH=/app
ENV PORT=8003

CMD ["python3", "app.py"]
