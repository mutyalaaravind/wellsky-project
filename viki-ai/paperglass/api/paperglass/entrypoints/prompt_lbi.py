import asyncio
import sys

from kink import inject

from paperglass.usecases.commands import PromptLBI
from paperglass.interface.ports import ICommandHandlingPort


@inject
async def main(label: str, question: str, command_handler: ICommandHandlingPort):
    command = PromptLBI(label=label, question=question)
    print('Command returned:', await command_handler.handle_command(command))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python prompt_lbi.py <label> <question>')
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
