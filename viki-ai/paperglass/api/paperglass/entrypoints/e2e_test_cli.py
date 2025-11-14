import asyncio
import sys, os
import json
from collections import OrderedDict
from kink import inject # type: ignore

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.domain.utils.uuid_utils import get_uuid4
from paperglass.usecases.e2e_v4_tests import TestHarness
from paperglass.log import getLogger
LOGGER = getLogger(__name__)

async def run():    
    await TestHarness().run(mode="sample", run_id=get_uuid4())
    #await TestHarness().run_test_only("87efe5aeefbd11efa07a42004e494300", "b4e1c25af06511efa3f71174f9a9c422", mode="test_only")

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()