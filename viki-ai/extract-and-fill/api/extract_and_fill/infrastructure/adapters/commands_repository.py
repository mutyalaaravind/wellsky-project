import uuid,json
from google.cloud.firestore import AsyncClient as AsyncFirestoreClient
from extract_and_fill.domain.commands import Command
from extract_and_fill.infrastructure.ports import ICommandsRepository

COLLECTION_NAME = "extract_commands"

class CommandsRepository(ICommandsRepository):
    
    def __init__(self, project_id, db_name) -> None:
        if db_name != "(default)":
            self.db = AsyncFirestoreClient(project=project_id, database=db_name)
        else:
            self.db = AsyncFirestoreClient()

    async def save(self, command: Command) -> None:
        doc_ref = self.db.collection(COLLECTION_NAME).document(uuid.uuid4().hex)
        print(command.json())
        await doc_ref.set(json.loads(command.json()))
        return True