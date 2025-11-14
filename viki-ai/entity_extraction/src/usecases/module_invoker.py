from models.general import TaskParameters, TaskResults
from modules.module_registry import registry

from util.custom_logger import getLogger
from util.exception import exceptionToMap

LOGGER = getLogger(__name__)

class ModuleInvoker:
    """Invoker for module-type tasks."""
    
    async def run(self, task_params: TaskParameters) -> TaskResults:
        """
        Run a module task with the given parameters.
        
        :param task_params: The parameters for the module task to run.
        :return: The processed task parameters after running the module.
        """
        module_type = task_params.task_config.module.type

        extra = {
            "task_params": task_params.dict()
        }

        LOGGER.debug(f"Running module task: {module_type}", extra=extra)
        
        try:
            # Get the module class from the registry
            module_class = registry.get_module(module_type)
            
            if module_class is None:
                available_modules = registry.list_modules()
                raise ValueError(f"Module '{module_type}' not found in registry. Available modules: {available_modules}")
            
            # Create an instance of the module
            module_instance = module_class()
            
            # Run the module with the task parameters
            LOGGER.debug(f"Executing module '{module_type}' with instance: {module_instance.__class__.__name__}", extra=extra)
            task_results = await module_instance.run(task_params)
            
            extra.update({"task_results": task_results.dict()})
            
            LOGGER.debug(f"Module task {module_type} completed successfully", extra=extra)
            return task_results
            
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error running module task {module_type}: {str(e)}", extra=extra)
            raise
