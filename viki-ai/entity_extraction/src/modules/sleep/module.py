from modules.imodule import IModule
from models.general import TaskParameters, TaskResults

from util.custom_logger import getLogger

LOGGER = getLogger(__name__)

class Sleep(IModule):
    """
    Sleep module for entity extraction.  Allows for testing and debugging of a pipeline by simulating a sleep period.
    """

    def __init__(self):
        super().__init__()

    async def run(self, task_params: TaskParameters) -> TaskResults:
        """
        Run the test module on the given task parameters.

        :param task_params: The task parameters for the module.
        :return: The task results after running the module.
        """
        extra = {
            "module_name": self.name,
            "task_params": task_params.model_dump()
        }

        sleepy_time = int(task_params.task_config.params.get("sleep", "10" ))

        LOGGER.info(f"Running Sleep module to sleep for {sleepy_time}s with parameters: {task_params.model_dump()}", extra=extra)
        LOGGER.debug(f"Sleep module sleeping for {sleepy_time}s...", extra=extra)

        # Simulate sleep for the specified time
        import asyncio
        await asyncio.sleep(sleepy_time)

        LOGGER.debug(f"Sleep module awakens after {sleepy_time}s...", extra=extra)        

        result_output = {
            "slept_seconds": sleepy_time
        }

        # Return TaskResults with the extracted entities
        return TaskResults(
            success=True,
            results=result_output,
            metadata=extra
        )
