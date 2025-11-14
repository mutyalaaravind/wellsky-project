FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy pyproject.toml and lock file
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync

# Copy application code
COPY ./src ./src

# Expose port
EXPOSE 19000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Run the application
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "19000"]
