# VIKI Shared

Shared utilities and models for VIKI AI projects.

## Overview

This package contains common functionality that is shared across multiple VIKI AI projects, including:

- **Models**: Base models and common domain objects
- **Utils**: JSON utilities, date functions, logging infrastructure, exception handling
- **Adapters**: Common adapter patterns

## Installation

For local development, install in editable mode:

```bash
pip install -e .
```

For development with all dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

```python
from viki_shared.utils.json_utils import JsonUtil
from viki_shared.utils.date_utils import now_utc
from viki_shared.utils.logger import getLogger
from viki_shared.models.base import AggBase

# Use shared utilities
logger = getLogger(__name__)
current_time = now_utc()
data = JsonUtil.clean({"timestamp": current_time})
```

## Structure

- `src/viki_shared/models/` - Base models and common domain objects
- `src/viki_shared/utils/` - Utility functions and classes
- `src/viki_shared/adapters/` - Common adapter patterns

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black src tests
isort src tests
```

Type checking:
```bash
mypy src
```