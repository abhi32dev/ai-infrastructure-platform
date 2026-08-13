# Production Dockerfile for Project 8 - vLLM & PagedAttention
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8007

ENV PYTHONPATH=/app
ENV PORT=8007

CMD ["python3", "app.py"]
