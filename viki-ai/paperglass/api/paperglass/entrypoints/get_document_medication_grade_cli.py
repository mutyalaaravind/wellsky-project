import asyncio
import sys, os
import json

from kink import inject

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.settings import get_module_root
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.infrastructure.ports import IQueryPort

import paperglass.usecases.documents as documents
from paperglass.domain.values import DocumentOperationType

from paperglass.usecases.commands import (
    PerformGrading
)


from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

@inject
async def run(commands: ICommandHandlingPort, query: IQueryPort):
   
    document_id = "b514a5c2628911efadd342004e494300"
    extracted_medication_id = "2f8750d0657411ef9926090279f3bd3c"
    document_operation_instance_id = "1805aa68657411ef9926090279f3bd3c"

    

    LOGGER.debug("extracted_medication_id: %s", extracted_medication_id)
    LOGGER.debug("document_operation_instance_id: %s", document_operation_instance_id)

    results = await query.get_extracted_medication_grades(document_id)
    LOGGER.debug('Results: %s', results)

    #results = await query.get_extracted_medication_grade_by_document_operation_instance(extracted_medication_id, document_operation_instance_id)
    #LOGGER.debug('Results: %s', results)

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()
