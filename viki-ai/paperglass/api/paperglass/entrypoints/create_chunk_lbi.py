import asyncio
import sys

from kink import inject

from paperglass.usecases.commands import CreateChunkLBI
from paperglass.interface.ports import ICommandHandlingPort


@inject
async def main(document_id: str, chunk_index: str, command_handler: ICommandHandlingPort):
    command = CreateChunkLBI(document_id=document_id, chunk_index=chunk_index)
    print('Command returned:', await command_handler.handle_command(command))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python create_chunk_lbi.py <chunk_index>')
        sys.exit(1)
    asyncio.run(main('0127d144e58711eea57cc3a190d5388c', int(sys.argv[1])))
