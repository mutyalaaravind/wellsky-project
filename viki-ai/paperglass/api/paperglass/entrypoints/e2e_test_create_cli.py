import asyncio
import sys, os
import json
from collections import OrderedDict
from kink import inject # type: ignore

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.usecases.e2e_v4_tests import TestHarness
from paperglass.log import getLogger
LOGGER = getLogger(__name__)

async def run():    
    document_id = "87efe5aeefbd11efa07a42004e494300"
    await TestHarness().create_testcase_from_document(document_id)

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()