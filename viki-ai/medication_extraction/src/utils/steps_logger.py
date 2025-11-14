from utils.json import DateTimeEncoder
from utils.custom_logger import getLogger

from models import Page,Document

import json

LOGGER = getLogger(__name__)

async def log_step(step_id:str, document:Document, page:Page, run_id:str, recovery_attempt:int, status:str, error:str=None):
    metadata = {}
    if document:
        metadata.update(document.dict())
    if page:
        metadata.update(page.dict())
    if error:
        metadata.update({"error":str(error)})
    metadata["run_id"] = run_id
    metadata["recovery_attempt"] = recovery_attempt
    metadata["status"] = status
    LOGGER.info(f"STEP_LOGGER|STEP:{step_id}|METADATA:{json.dumps(metadata, indent=2, cls=DateTimeEncoder)}")