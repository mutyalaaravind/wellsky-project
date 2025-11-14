import asyncio
import json
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.usecases.commands import ImportHostAttachmentFromExternalStorageUri
from paperglass.interface.ports import ICommandHandlingPort
import paperglass.usecases.documents as documents

from paperglass.infrastructure.adapters.external_medications import HHHAdapter
from paperglass.domain.values import HostFreeformMedicationAddModel, Result

from kink import inject
from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

@inject
async def import_attachment(gcs_uri:str,command_handler:ICommandHandlingPort):
    """
    Import attachment from GCS to Firestore
    """
    LOGGER.info(f"Importing attachment from GCS: {gcs_uri}")
    resut:Result = await command_handler.handle_command(ImportHostAttachmentFromExternalStorageUri(
        app_id="hhh",
        external_storage_uri=gcs_uri,
        raw_event={"hey":"there"}
    ))
    print(resut.dict())
    

if __name__ == '__main__':
    asyncio.run(import_attachment("gs://wsh-monolith_attachment-dev/AMDocuments2/9381/20240725134008Medcation1.jpg"))