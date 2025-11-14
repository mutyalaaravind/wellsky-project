from ..usecases.commands import Command
from ..domain.events import Event


class CommandError(Exception):
    pass


class ICommandHandlingPort:  # pragma: no cover
    """
    Interface to process incoming commands.
    """

    async def handle_command(self, command: Command):
        pass
    
    async def handle_command_with_explicit_transaction(self, command: Command):
        pass
    
class IMedispanMatchCommandHandlingPort:
    
    """
    Interface to process incoming medispan match commands.
    """

    async def handle_command(self, command: Command):
        pass


class IEventHandlingPort:  # pragma: no cover
    """
    Interface to handle domain events (such as deliveries that are pending processing).
    """

    async def handle_event(self, event: Event):
        raise NotImplementedError()
