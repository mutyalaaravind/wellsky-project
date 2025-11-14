# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy pyproject.toml and lock file
COPY admin/api/pyproject.toml admin/api/uv.lock ./

# Copy shared package including egg-info
COPY shared /app/shared

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
COPY admin/api/src ./admin

# Expose port
EXPOSE 14000

# Environment variables
ENV PYTHONUNBUFFERED=1

WORKDIR /app/admin

# Run the application
CMD ["uv", "run", "uvicorn",  "main:app", "--host", "0.0.0.0", "--port", "14000"]