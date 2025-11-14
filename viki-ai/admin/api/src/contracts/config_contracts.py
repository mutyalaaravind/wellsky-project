"""
Config Contracts for Admin API.

This module defines the port interface for configuration access.
"""

from abc import ABC, abstractmethod


class ConfigPort(ABC):
    """Port interface for configuration access."""
    
    @abstractmethod
    async def get_config(self):
        """
        Get the admin configuration.
        
        Returns:
            SystemConfig: The configuration aggregate
        """
        pass