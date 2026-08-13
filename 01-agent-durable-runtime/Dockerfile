# Production Dockerfile for Project 1 - Agent Runtime & MCP Protocol
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONPATH=/app
ENV PORT=8000

CMD ["python3", "app.py"]
