# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy pyproject.toml and lock file
COPY pyproject.toml uv.lock ./

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Use uv to sync dependencies
RUN uv sync

# Copy application code
COPY ./src ./cloudtask_emulator

# Expose port
EXPOSE 30001

# Environment variables
ENV PYTHONUNBUFFERED=1

WORKDIR /app/cloudtask_emulator

# Run the application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "30001"]
