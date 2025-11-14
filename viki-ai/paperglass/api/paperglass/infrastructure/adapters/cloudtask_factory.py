from paperglass.infrastructure.ports import ICloudTaskPort
from paperglass.infrastructure.adapters.google import CloudTaskAdapter
from paperglass.infrastructure.adapters.cloudtask_emulator_adapter import CloudTaskEmulatorAdapter
from paperglass.settings import CLOUD_PROVIDER, CLOUDTASK_EMULATOR_ENABLED, CLOUDTASK_EMULATOR_URL, GCP_PROJECT_ID
from paperglass.log import getLogger

LOGGER = getLogger(__name__)


def create_cloud_task_adapter() -> ICloudTaskPort:
    """
    Factory function to create the appropriate CloudTask adapter based on configuration.
    
    Returns:
        ICloudTaskPort: Either CloudTaskAdapter or CloudTaskEmulatorAdapter
    """
    if CLOUD_PROVIDER == "local" and CLOUDTASK_EMULATOR_ENABLED:
        LOGGER.info(f"Using CloudTaskEmulatorAdapter with emulator URL: {CLOUDTASK_EMULATOR_URL}")
        return CloudTaskEmulatorAdapter(
            project_id=GCP_PROJECT_ID,
            emulator_url=CLOUDTASK_EMULATOR_URL
        )
    else:
        LOGGER.info(f"Using CloudTaskAdapter for cloud provider: {CLOUD_PROVIDER}")
        return CloudTaskAdapter(project_id=GCP_PROJECT_ID)
