"""
This module tells injector how to map driving ports to use cases.
Importing the classes makes them register as injectable.
"""
from kink import di
# from paperglass.usecases.medispan_command_handling import MedispanCommandHandlingUseCase

from ..usecases.command_handling import CommandHandlingUseCase
from ..usecases.event_handling import EventHandlingUseCase

from .ports import ICommandHandlingPort, IEventHandlingPort

di[ICommandHandlingPort] = lambda di: CommandHandlingUseCase()
di[IEventHandlingPort] = lambda di: EventHandlingUseCase()
#di[IMedispanMatchCommandHandlingPort] = lambda di: MedispanCommandHandlingUseCase()
