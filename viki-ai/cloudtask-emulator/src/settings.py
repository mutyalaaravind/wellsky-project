import os
from typing import Optional

# Cloud Task Emulator Configuration
CLOUDTASK_EMULATOR_PORT: int = int(os.getenv("CLOUDTASK_EMULATOR_PORT", "30001"))
CLOUDTASK_EMULATOR_HOST: str = os.getenv("CLOUDTASK_EMULATOR_HOST", "0.0.0.0")

# Task Processing Configuration
MAX_RETRIES: int = int(os.getenv("CLOUDTASK_MAX_RETRIES", "3"))
RETRY_BASE_DELAY: int = int(os.getenv("CLOUDTASK_RETRY_BASE_DELAY", "2"))
MAX_RETRY_DELAY: int = int(os.getenv("CLOUDTASK_MAX_RETRY_DELAY", "60"))

# Worker Configuration
WORKER_CHECK_INTERVAL: float = float(os.getenv("CLOUDTASK_WORKER_CHECK_INTERVAL", "0.1"))
WORKER_ERROR_DELAY: float = float(os.getenv("CLOUDTASK_WORKER_ERROR_DELAY", "5.0"))

# HTTP Client Configuration
HTTP_TIMEOUT: int = int(os.getenv("CLOUDTASK_HTTP_TIMEOUT", "180"))

# Logging Configuration
LOG_LEVEL: str = os.getenv("CLOUDTASK_LOG_LEVEL", "INFO")

# Development/Debug Configuration
DEBUG: bool = os.getenv("CLOUDTASK_DEBUG", "false").lower() in ("true", "1", "yes")
