# Production Dockerfile for Project 10 - NVIDIA Triton GPU Scheduler
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8009

ENV PYTHONPATH=/app
ENV PORT=8009

CMD ["python3", "app.py"]
