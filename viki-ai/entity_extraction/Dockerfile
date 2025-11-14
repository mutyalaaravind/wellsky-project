# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy pyproject.toml and lock file
COPY pyproject.toml uv.lock ./

# Final stage
# FROM python:3.11-slim

#WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    ca-certificates \
    curl \
    netcat-traditional \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN uv sync

# Copy application code
COPY ./src ./entity_extraction

# Expose port
EXPOSE 18000

# Environment variables
ENV PYTHONUNBUFFERED=1

WORKDIR /app/entity_extraction

# Run the application
CMD ["uv", "run", "uvicorn",  "main:app", "--host", "0.0.0.0", "--port", "18000"]
