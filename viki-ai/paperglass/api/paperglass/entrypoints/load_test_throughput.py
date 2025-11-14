import sys, os
import asyncio
import aiohttp
import time

from google.cloud import monitoring_v3
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.log import getLogger, labels, CustomLogger
LOGGER = CustomLogger(__name__)

# Define the endpoint and headers
LOCAL_HOST = "localhost:15000"
DEV_HOST = "ai-paperglass-api-zqftmopgsq-uk.a.run.app" # DEV
QA_HOST = "ai-paperglass-api-p32qledfyq-uk.a.run.app" # QA
STAGE_HOST = "ai-paperglass-api-zzygbs3ypa-uk.a.run.app" # STAGE

PROJECT_ID = "viki-stage-app"

ANNOTATIONS_ENABLED = False

# SETTINGS --------------------------------------------------------------------------------
HOST = STAGE_HOST
NO_OF_DOCS_PER_MINUTE = 80

LOADTEST_TYPE = "default" 
#LOADTEST_TYPE = "vertex-ai" # default, vertex-ai
#DOCUMENT_ID = "72420dccb5b111efb38a42004e494300" # Needed for type vertex-ai  #Stage (batch_size=20) doc_id: 72420dccb5b111efb38a42004e494300
# ------------------------------------------------------------------------------------------

url = f"https://{HOST}/api/orchestrate/medication_extraction/loadtest/poke"
if LOADTEST_TYPE == "vertex-ai":
    url = url + f"?loadtest_type={LOADTEST_TYPE}&document_id={DOCUMENT_ID}"

#THROUGHPUT_MS = 10000  # Drop document Every 10 seconds
SLEEP_TIME = 60 / NO_OF_DOCS_PER_MINUTE  # Drop document Every 60 seconds

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6IjAwNyIsInRlbmFudElkIjoiNTQzMjEiLCJwYXRpZW50SWQiOiIyOTQzN2RkMjRmZmU0NjVlYjYxMWE2MWIwYjYyZjYwOCIsImFtdXNlcmtleSI6IjEyMzQ1In0.nNHPgG08X_YqaBN1spIKq2j0xTRT3vQmXhv-rOZ8JAU",
    "Content-Type": "application/json"
}

# Define the payload
payload = {
    "iteration_key": "1",
    "labels": ["loadtest"],
    "campaign_id": "test_campaign_001"
}

def create_annotation(description, labels={}):
    annotation_labels = {
        "owner": "balki",
        "business-unit": "viki",
        "environment": "stage",
        "application": "",
        "service": ""
    }
    annotation_labels.update(labels)

    project_id = PROJECT_ID
    client = monitoring_v3.NotificationChannelServiceClient()
    project_name = f"projects/{project_id}"
    now = datetime.utcnow()
    timestamp = Timestamp()
    timestamp.FromDatetime(now)

    annotation = monitoring_v3.NotificationChannel(
        display_name="Load Test",
        description=description,
        labels=labels,
        creation_record=monitoring_v3.MutationRecord(mutate_time=timestamp)
    )

    client.create_notification_channel(name=project_name, notification_channel=annotation)

async def post_request(session):
    async with session.post(url, json=payload, headers=headers) as response:
        if response.status == 200:
            LOGGER.info(f"Request successful: {await response.text()}")
        else:
            LOGGER.info(f"Request failed with status: {response.status}")

async def main():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        idx = 0

        if ANNOTATIONS_ENABLED:
            create_annotation(f"Load Test start {NO_OF_DOCS_PER_MINUTE} docs/min")

        LOGGER.info(f"Sleeping for {SLEEP_TIME} seconds")
        while True:
            LOGGER.info("Sending request: %s", idx)
            payload["iteration_key"] = str(idx)
            asyncio.create_task(post_request(session))
            await asyncio.sleep(SLEEP_TIME) 
            idx += 1

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Exiting load test script")
        if ANNOTATIONS_ENABLED:
            create_annotation(f"Load Test end {NO_OF_DOCS_PER_MINUTE} docs/min")
        sys.exit(0)