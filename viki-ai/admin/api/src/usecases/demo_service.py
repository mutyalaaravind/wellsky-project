from typing import List, Optional
from kink import inject

from model_aggregates.demo_subjects import DemoSubjectAggregate, DemoSubjectsConfigAggregate
from infrastructure.demo_ports import IDemoSubjectRepository, ICommandHandlingPort
from usecases.demo_commands import (
    CreateDemoSubjectCommand,
    UpdateDemoSubjectCommand, 
    DeleteDemoSubjectCommand,
    UpdateSubjectConfigCommand,
    GetDemoSubjectsQuery,
    GetDemoSubjectQuery,
    GetSubjectConfigQuery
)


@inject
class DemoSubjectService(ICommandHandlingPort):
    """Service for handling demo subject commands and queries"""

    def __init__(self, repository: IDemoSubjectRepository):
        self.repository = repository

    # Command handlers
    async def handle_create_demo_subject(self, command: CreateDemoSubjectCommand) -> DemoSubjectAggregate:
        """Handle create demo subject command"""
        # Ensure config exists
        config = await self.repository.get_subject_config(command.app_id)
        if not config:
            config = DemoSubjectsConfigAggregate.create(command.app_id)
            await self.repository.save_subject_config(config)

        # Create new subject
        subject = DemoSubjectAggregate.create(command.app_id, command.name)
        return await self.repository.save_subject(subject)

    async def handle_update_demo_subject(self, command: UpdateDemoSubjectCommand) -> DemoSubjectAggregate:
        """Handle update demo subject command"""
        subject = await self.repository.get_subject(command.app_id, command.subject_id)
        if not subject:
            raise ValueError(f"Subject {command.subject_id} not found")
        
        if subject.is_deleted:
            raise ValueError("Cannot update deleted subject")

        subject.update_name(command.name)
        return await self.repository.save_subject(subject)

    async def handle_delete_demo_subject(self, command: DeleteDemoSubjectCommand) -> bool:
        """Handle delete demo subject command"""
        subject = await self.repository.get_subject(command.app_id, command.subject_id)
        if not subject or subject.is_deleted:
            return False

        subject.soft_delete()
        await self.repository.save_subject(subject)
        return True

    async def handle_update_subject_config(self, command: UpdateSubjectConfigCommand) -> DemoSubjectsConfigAggregate:
        """Handle update subject config command"""
        config = await self.repository.get_subject_config(command.app_id)
        if not config:
            config = DemoSubjectsConfigAggregate.create(command.app_id, command.label)
        else:
            config.update_label(command.label)
        
        return await self.repository.save_subject_config(config)

    # Query handlers
    async def get_demo_subjects(self, query: GetDemoSubjectsQuery) -> List[DemoSubjectAggregate]:
        """Get demo subjects for an app"""
        return await self.repository.list_subjects(query.app_id)

    async def get_demo_subject(self, query: GetDemoSubjectQuery) -> Optional[DemoSubjectAggregate]:
        """Get a specific demo subject"""
        subject = await self.repository.get_subject(query.app_id, query.subject_id)
        if subject and not subject.is_deleted:
            return subject
        return None

    async def get_subject_config(self, query: GetSubjectConfigQuery) -> DemoSubjectsConfigAggregate:
        """Get or create subject configuration"""
        config = await self.repository.get_subject_config(query.app_id)
        if not config:
            config = DemoSubjectsConfigAggregate.create(query.app_id)
            await self.repository.save_subject_config(config)
        return config