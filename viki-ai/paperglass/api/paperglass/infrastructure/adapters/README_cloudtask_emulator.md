# CloudTask Emulator Setup for Paperglass

This document explains how to use the CloudTask Emulator with Paperglass for local development.

## Overview

Paperglass now supports automatic switching between the real Google Cloud Tasks service and a local CloudTask Emulator based on configuration settings. This allows for easier local development and testing without requiring actual GCP resources.

## Configuration

The system automatically selects the appropriate adapter based on these environment variables:

- `CLOUD_PROVIDER`: Set to "local" for local development
- `CLOUDTASK_EMULATOR_ENABLED`: Set to "true" to enable the emulator
- `CLOUDTASK_EMULATOR_URL`: URL of the running emulator (default: "http://localhost:30001")

## Usage

### For Local Development (with Emulator)

Set these environment variables:
```bash
CLOUD_PROVIDER=local
CLOUDTASK_EMULATOR_ENABLED=true
CLOUDTASK_EMULATOR_URL=http://localhost:30001
```

The system will automatically use `CloudTaskEmulatorAdapter` which communicates with the cloudtask emulator service.

### For Production/Cloud (with Real Cloud Tasks)

Set these environment variables:
```bash
CLOUD_PROVIDER=google  # or any value other than "local"
CLOUDTASK_EMULATOR_ENABLED=false  # optional, any value other than "true"
```

The system will automatically use `CloudTaskAdapter` which communicates with real Google Cloud Tasks.

## How It Works

1. **Factory Pattern**: The `create_cloud_task_adapter()` function in `cloudtask_factory.py` automatically selects the right adapter based on configuration.

2. **Dependency Injection**: The factory is used in `bindings.py` to provide the correct implementation:
   ```python
   di[ICloudTaskPort] = lambda _: create_cloud_task_adapter()
   ```

3. **Interface Compatibility**: Both adapters implement the same `ICloudTaskPort` interface, so the rest of the application code doesn't need to change.

## Starting the CloudTask Emulator

Make sure the cloudtask emulator service is running on the configured URL (default: http://localhost:30001) when using local mode.

## Logging

The factory logs which adapter is being used:
- "Using CloudTaskEmulatorAdapter with emulator URL: ..." for local mode
- "Using CloudTaskAdapter for cloud provider: ..." for cloud mode

This helps with debugging and ensures you know which mode you're running in.
