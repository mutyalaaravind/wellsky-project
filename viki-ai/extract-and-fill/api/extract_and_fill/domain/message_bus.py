# pylint: disable=broad-except, attribute-defined-outside-init
# from __future__ import annotations
import logging
from typing import Callable, Dict, List, Union, Type, TYPE_CHECKING
import extract_and_fill.domain.commands as commands
import extract_and_fill.domain.events as events

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


class MessageBus(object):

    def __init__(
        self,
        event_handlers: Dict[Type[events.Event], List[Callable]],
        command_handlers: Dict[Type[commands.Command], Callable],
    ):
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    async def handle(self, message: Message):
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            logger.debug('handling message %s ', message)
            if isinstance(message, events.Event):
                return await self.handle_event(message)
            elif isinstance(message, commands.Command):
                return await self.handle_command(message)
            else:
                raise Exception(f'{message} was not an Event or Command')

    async def handle_event(self, event: events.Event):
        for handler in self.event_handlers[type(event)]:
            try:
                logger.debug('handling event %s with handler %s', event, handler)
                return await handler(event)
            except Exception:
                logger.exception('Exception handling event %s', event)
                continue

    async def handle_command(self, command: commands.Command):
        for handler in self.command_handlers[type(command)]:
            try:
                logger.debug('handling command %s with handler %s', command, handler)
                return await handler(command)
            except Exception:
                logger.exception('Exception handling command %s', command)
                continue
