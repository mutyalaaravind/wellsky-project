import os
import importlib
import inspect
from pathlib import Path


class ModuleRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModuleRegistry, cls).__new__(cls)
            cls._instance.modules = {}
            cls._instance._auto_discovered = False
        return cls._instance

    def register_module(self, module_name, module_class):
        if module_name in self.modules:
            raise ValueError(f"Module '{module_name}' is already registered.")
        self.modules[module_name] = module_class

    def get_module(self, module_name):
        # Auto-discover modules if not done yet
        if not self._auto_discovered:
            self._auto_discover_modules()
        return self.modules.get(module_name)

    def list_modules(self):
        # Auto-discover modules if not done yet
        if not self._auto_discovered:
            self._auto_discover_modules()
        return list(self.modules.keys())

    def _auto_discover_modules(self):
        """Automatically discover and import all modules in the modules directory."""
        if self._auto_discovered:
            return
            
        try:
            # Get the modules directory path
            modules_dir = Path(__file__).parent
            
            # Scan for Python files in subdirectories
            for subdir in modules_dir.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('__'):
                    # Look for Python files in the subdirectory
                    for py_file in subdir.glob('*.py'):
                        if py_file.name != '__init__.py':
                            # Import the module
                            module_path = f"modules.{subdir.name}.{py_file.stem}"
                            try:
                                importlib.import_module(module_path)
                            except ImportError as e:
                                # Log the error but continue with other modules
                                print(f"Warning: Could not import module {module_path}: {e}")
                                
            self._auto_discovered = True
            
        except Exception as e:
            print(f"Error during module auto-discovery: {e}")
            self._auto_discovered = True  # Mark as attempted to avoid infinite loops


# Global registry instance
registry = ModuleRegistry()
