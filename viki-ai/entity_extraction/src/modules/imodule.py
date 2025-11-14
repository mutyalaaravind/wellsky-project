import os
import inspect
from models.general import TaskParameters, TaskResults
from util.custom_logger import getLogger


class ModuleRegistryMeta(type):
    """Metaclass that automatically registers IModule implementations."""
    
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        
        # Only register classes that inherit from IModule (not IModule itself)
        # Check if any base class has the name 'IModule'
        if bases and any(base.__name__ == 'IModule' for base in bases):
            from modules.module_registry import registry
            # Create an instance to get the auto-generated name
            instance = new_class()
            registry.register_module(instance.name, new_class)
        
        return new_class


class IModule(metaclass=ModuleRegistryMeta):
    """
    Interface for modules that can be used in the entity extraction pipeline.
    """

    def __init__(self, name: str = None):
        if name is None:
            # Use stack inspection to find the calling file (the implementation)
            frame = inspect.currentframe().f_back
            caller_file = frame.f_code.co_filename
            name = os.path.basename(os.path.dirname(caller_file))
        self.name = name
        self.logger = getLogger(f"modules.{self.name}")

    async def run(self, task_params: TaskParameters) -> TaskResults:
        """
        Run the module on the given task parameters.

        :param task_params: The task parameters for the module.
        :return: The task results after running the module.
        """
        raise NotImplementedError("Subclasses should implement this method.")
