# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY uv.lock ./
COPY main.py ./
COPY server.py ./
COPY data/ ./data/
COPY tools/ ./tools/
COPY utils/ ./utils/

# Install dependencies using uv
RUN uv sync --frozen

# Expose port (MCP typically uses stdio, but this allows for HTTP if needed)
EXPOSE 8000

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the MCP server
CMD ["uv", "run", "python", "main.py"]
