from modules.imodule import IModule
from models.general import TaskParameters, TaskResults

class Test(IModule):
    """
    Test module for entity extraction.
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

        message = task_params.params.get("output", f"Running Test module: {self.name}")
        message = message.format(**task_params.context)

        self.logger.info(message, extra=extra)

        result_output = {
            "output": message
        }

        # Return TaskResults with the extracted entities
        return TaskResults(
            success=True,
            results=result_output,
            metadata=extra
        )
