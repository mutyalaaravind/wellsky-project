import asyncio
import datetime
import json
import sys,os
import time
from typing import Dict
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from kink import inject
from paperglass.settings import APPLICATION_INTEGRATION_TRIGGER_ID, CLOUD_TASK_QUEUE_NAME, INTEGRATION_PROJECT_NAME, SELF_API, SERVICE_ACCOUNT_EMAIL
from paperglass.usecases.commands import CreateDocument, TriggerExtraction
from paperglass.infrastructure.ports import IApplicationIntegration, IQueryPort
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.domain.models import Document
from paperglass.domain.values import DocumentStatusType
from google.cloud import storage
from mktoken import mktoken, mktoken2
import csv

import math
from google.cloud import firestore
import csv
from paperglass.domain.time import now_utc

@inject
async def load_test(command_handler: ICommandHandlingPort, query_port: IQueryPort, integration: IApplicationIntegration):
    app_id="007"
    tenant_id="54321"
    # dev: 134ac09db971428e86559833919f7cc7
    # stage: 08b7d03d312f4483b74e088cac893247

    now = now_utc()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    campaign_id = "load_test_" + now_str
    metadata = {
        "labels": ["loadtest"],
        "campaign_id": campaign_id,
    }

    patient_id="5ad3d2c003c24c47ae14af17fda071e6"
    for i in range(1, 11):
        thismeta = metadata.copy()
        thismeta["iteration"] = i
        with open('./.logs/load_test_2_10_pages.pdf', 'rb') as f:
            file_content = f.read()
            await command_handler.handle_command(CreateDocument(
                app_id=app_id,
                tenant_id=tenant_id,
                patient_id=patient_id, #dev: Test Automation patient
                file_name=f"load_test_{i}.pdf",
                file=file_content,
                token=mktoken2(app_id, tenant_id, patient_id),
                metadata=thismeta
            ))
            
    
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Load test for the extraction process')
    #parser.add_argument('--project', required=True, help='Project name')
    asyncio.run(load_test())