# Production Dockerfile for Project 5 - Event Stream & PySpark ETL
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8004

ENV PYTHONPATH=/app
ENV PORT=8004

CMD ["python3", "app.py"]
