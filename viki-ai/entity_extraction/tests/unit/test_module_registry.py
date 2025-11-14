"""
Unit tests for modules.module_registry module.
"""

import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import importlib
from src.modules.module_registry import ModuleRegistry, registry


@pytest.fixture
def fresh_registry():
    """Create a fresh registry instance for testing."""
    # Reset the singleton instance
    ModuleRegistry._instance = None
    fresh_reg = ModuleRegistry()
    fresh_reg.modules = {}
    fresh_reg._auto_discovered = False
    return fresh_reg


def test_singleton_pattern():
    """Test that ModuleRegistry follows singleton pattern."""
    registry1 = ModuleRegistry()
    registry2 = ModuleRegistry()
    
    assert registry1 is registry2
    assert id(registry1) == id(registry2)


def test_register_module(fresh_registry):
    """Test registering a module."""
    class TestModule:
        pass
    
    fresh_registry.register_module("test_module", TestModule)
    
    assert "test_module" in fresh_registry.modules
    assert fresh_registry.modules["test_module"] is TestModule


def test_register_duplicate_module(fresh_registry):
    """Test that registering duplicate module raises error."""
    class TestModule1:
        pass
    
    class TestModule2:
        pass
    
    fresh_registry.register_module("test_module", TestModule1)
    
    with pytest.raises(ValueError, match="Module 'test_module' is already registered"):
        fresh_registry.register_module("test_module", TestModule2)


def test_get_module_without_auto_discovery(fresh_registry):
    """Test getting a manually registered module."""
    class TestModule:
        pass
    
    fresh_registry.register_module("test_module", TestModule)
    fresh_registry._auto_discovered = True  # Skip auto discovery
    
    result = fresh_registry.get_module("test_module")
    assert result is TestModule


def test_get_nonexistent_module(fresh_registry):
    """Test getting a module that doesn't exist."""
    fresh_registry._auto_discovered = True  # Skip auto discovery
    
    result = fresh_registry.get_module("nonexistent_module")
    assert result is None


@patch('src.modules.module_registry.importlib.import_module')
@patch('src.modules.module_registry.Path')
def test_auto_discover_modules(mock_path, mock_import, fresh_registry):
    """Test auto discovery of modules."""
    # Mock the directory structure
    mock_modules_dir = MagicMock()
    mock_path.return_value.parent = mock_modules_dir
    
    # Mock subdirectories
    mock_subdir1 = MagicMock()
    mock_subdir1.is_dir.return_value = True
    mock_subdir1.name = "test_module1"
    
    mock_subdir2 = MagicMock()
    mock_subdir2.is_dir.return_value = True
    mock_subdir2.name = "test_module2"
    
    mock_hidden_dir = MagicMock()
    mock_hidden_dir.is_dir.return_value = True
    mock_hidden_dir.name = "__pycache__"
    
    mock_modules_dir.iterdir.return_value = [mock_subdir1, mock_subdir2, mock_hidden_dir]
    
    # Mock Python files in subdirectories
    mock_py_file1 = MagicMock()
    mock_py_file1.name = "module.py"
    mock_py_file1.stem = "module"
    
    mock_init_file = MagicMock()
    mock_init_file.name = "__init__.py"
    
    mock_subdir1.glob.return_value = [mock_py_file1, mock_init_file]
    mock_subdir2.glob.return_value = []
    
    # Test auto discovery
    fresh_registry._auto_discover_modules()
    
    # Verify import_module was called for the right module
    mock_import.assert_called_once_with("modules.test_module1.module")
    assert fresh_registry._auto_discovered is True


@patch('src.modules.module_registry.importlib.import_module')
@patch('src.modules.module_registry.Path')
def test_auto_discover_with_import_error(mock_path, mock_import, fresh_registry, capsys):
    """Test auto discovery handles import errors gracefully."""
    # Mock the directory structure
    mock_modules_dir = MagicMock()
    mock_path.return_value.parent = mock_modules_dir
    
    mock_subdir = MagicMock()
    mock_subdir.is_dir.return_value = True
    mock_subdir.name = "broken_module"
    
    mock_modules_dir.iterdir.return_value = [mock_subdir]
    
    mock_py_file = MagicMock()
    mock_py_file.name = "module.py"
    mock_py_file.stem = "module"
    
    mock_subdir.glob.return_value = [mock_py_file]
    
    # Mock import error
    mock_import.side_effect = ImportError("Module not found")
    
    # Test auto discovery
    fresh_registry._auto_discover_modules()
    
    # Check that warning was printed
    captured = capsys.readouterr()
    assert "Warning: Could not import module modules.broken_module.module" in captured.out
    assert fresh_registry._auto_discovered is True


@patch('src.modules.module_registry.Path')
def test_auto_discover_with_general_error(mock_path, fresh_registry, capsys):
    """Test auto discovery handles general errors gracefully."""
    # Mock path to raise an exception
    mock_path.side_effect = Exception("File system error")
    
    # Test auto discovery
    fresh_registry._auto_discover_modules()
    
    # Check that error was printed and discovery marked as attempted
    captured = capsys.readouterr()
    assert "Error during module auto-discovery" in captured.out
    assert fresh_registry._auto_discovered is True


def test_get_module_triggers_auto_discovery(fresh_registry):
    """Test that get_module triggers auto discovery when needed."""
    with patch.object(fresh_registry, '_auto_discover_modules') as mock_discover:
        fresh_registry.get_module("test_module")
        mock_discover.assert_called_once()


def test_list_modules_triggers_auto_discovery(fresh_registry):
    """Test that list_modules triggers auto discovery when needed."""
    with patch.object(fresh_registry, '_auto_discover_modules') as mock_discover:
        fresh_registry.list_modules()
        mock_discover.assert_called_once()


def test_list_modules_returns_module_names(fresh_registry):
    """Test that list_modules returns correct module names."""
    class TestModule1:
        pass
    
    class TestModule2:
        pass
    
    fresh_registry.register_module("module1", TestModule1)
    fresh_registry.register_module("module2", TestModule2)
    fresh_registry._auto_discovered = True  # Skip auto discovery
    
    modules = fresh_registry.list_modules()
    assert set(modules) == {"module1", "module2"}


def test_auto_discover_already_discovered(fresh_registry):
    """Test that auto discovery is skipped if already done."""
    fresh_registry._auto_discovered = True
    
    with patch('src.modules.module_registry.Path') as mock_path:
        fresh_registry._auto_discover_modules()
        mock_path.assert_not_called()


def test_global_registry_instance():
    """Test that the global registry instance exists."""
    assert isinstance(registry, ModuleRegistry)


def test_new_method_initialization():
    """Test that __new__ method properly initializes attributes."""
    # Reset singleton
    ModuleRegistry._instance = None
    
    reg = ModuleRegistry()
    assert hasattr(reg, 'modules')
    assert hasattr(reg, '_auto_discovered')
    assert isinstance(reg.modules, dict)
    assert reg._auto_discovered is False