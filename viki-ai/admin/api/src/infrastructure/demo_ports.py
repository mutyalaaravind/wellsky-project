from abc import ABC, abstractmethod
from typing import List, Optional
from model_aggregates.demo_subjects import DemoSubjectAggregate, DemoSubjectsConfigAggregate


class IDemoSubjectRepository(ABC):
    """Port for demo subject repository"""

    @abstractmethod
    async def get_subject_config(self, app_id: str) -> Optional[DemoSubjectsConfigAggregate]:
        """Get subject configuration for an app"""
        pass

    @abstractmethod
    async def save_subject_config(self, config: DemoSubjectsConfigAggregate) -> DemoSubjectsConfigAggregate:
        """Save subject configuration"""
        pass

    @abstractmethod
    async def get_subject(self, app_id: str, subject_id: str) -> Optional[DemoSubjectAggregate]:
        """Get a specific demo subject"""
        pass

    @abstractmethod
    async def save_subject(self, subject: DemoSubjectAggregate) -> DemoSubjectAggregate:
        """Save a demo subject"""
        pass

    @abstractmethod
    async def list_subjects(self, app_id: str) -> List[DemoSubjectAggregate]:
        """List all non-deleted subjects for an app"""
        pass

    @abstractmethod
    async def delete_subject(self, app_id: str, subject_id: str) -> bool:
        """Delete a subject (returns True if found and deleted)"""
        pass


class ICommandHandlingPort(ABC):
    """Port for command handling"""

    @abstractmethod
    async def handle_create_demo_subject(self, command) -> DemoSubjectAggregate:
        """Handle create demo subject command"""
        pass

    @abstractmethod
    async def handle_update_demo_subject(self, command) -> DemoSubjectAggregate:
        """Handle update demo subject command"""
        pass

    @abstractmethod
    async def handle_delete_demo_subject(self, command) -> bool:
        """Handle delete demo subject command"""
        pass

    @abstractmethod
    async def handle_update_subject_config(self, command) -> DemoSubjectsConfigAggregate:
        """Handle update subject config command"""
        pass