import sys, os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import pytest

from paperglass.usecases.commands import (
    CreateEvidence
)
from kink import inject
from paperglass.infrastructure import bindings
from paperglass.infrastructure.ports import IQueryPort
from paperglass.interface.ports import ICommandHandlingPort
import asyncio
import pytest_asyncio

@pytest.fixture
def commands():
    @inject
    def get_commands(commands: ICommandHandlingPort):
        return commands

    return get_commands()

@pytest.fixture
def query():
    @inject
    def get_query(query: IQueryPort):
        return query

    return get_query()

@pytest.mark.asyncio
async def test_evidence_creation(commands,query):
    medications = await query.get_medications_by_document("e369244e23b311efa1920242ac120005")
    medication_list = []
    for medication in medications:
        medication_string = ""
        for k,v in medication.items():
            if k in ["name", "dosage", "frequency", "route","start_date","end_date","reason"]:
                medication_string = medication_string + k + ":" + (str(v) if v else "") + ","
        medication_list.append(medication_string)
    result = await commands.handle_command(CreateEvidence(app_id="007", 
                                            tenant_id="54321", 
                                            patient_id="aabafd7576d5403ba15a4094df83cb1b", 
                                            document_id="e369244e23b311efa1920242ac120005",
                                            page_id="02359dda23b411ef830c3e3297f4bd06",
                                            page_number=3,
                                            medications=medication_list
                                        )
                                    )
    
    assert result