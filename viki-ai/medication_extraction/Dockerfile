# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy pyproject.toml and lock file
COPY pyproject.toml uv.lock ./

# Use uv to install dependencies from lock file
# RUN uv pip sync uv.lock --system

# RUN uv pip install . --system
# RUN pip install uvicorn hypercorn



# Final stage
# FROM python:3.11-slim

#WORKDIR /app

# Install necessary system dependencies for google cloud
RUN apt-get update && apt-get install -y \
    gcc \
    ca-certificates \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN uv sync

# Copy installed packages from builder
# COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copy application code
COPY ./src ./medication_extraction

# Expose port
EXPOSE 17000

# Environment variables
ENV PYTHONUNBUFFERED=1

WORKDIR /app/medication_extraction

# Run the application
CMD ["uv", "run", "uvicorn",  "main:app", "--host", "0.0.0.0", "--port", "17000"]
