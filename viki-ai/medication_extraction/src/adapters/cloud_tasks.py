
from datetime import datetime
import json
from typing import Dict
from utils.json import DateTimeEncoder
from utils.custom_logger import getLogger

LOGGER = getLogger(__name__)

class CloudTaskAdapter:

    def __init__(self, project_id:str):
        self.project_id = project_id

    async def create_task(self, token, location, service_account_email, queue, url, payload):
        from google.cloud import tasks_v2
        from proto.message import MessageToDict

        extra = {            
            "queue": queue,
            "url": url,
            "payload": payload,
            "token": token,
        }
        LOGGER.info(f"Creating task for queue: {queue}, url: {url}, payload: {payload}", extra=extra)

        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(self.project_id, location, queue)
        task = {
                    "http_request": {  
                        "http_method": tasks_v2.HttpMethod.POST,
                        'url': url,
                        "oidc_token": {"service_account_email": service_account_email},
                        "headers": {"Content-Type": "application/json","Authorization2":'Bearer ' + token} if token else {"Content-Type": "application/json"},
                        "body":json.dumps(payload,cls=DateTimeEncoder).encode(),
                    }
                }        
        response = client.create_task(request={"parent": parent, "task": task})
        # Create a copy of task for logging that excludes the bytes body
        task_for_logging = task.copy()
        task_for_logging["http_request"] = task["http_request"].copy()
        task_for_logging["http_request"]["body"] = json.dumps(payload, cls=DateTimeEncoder)  # Use JSON string instead of encoded bytes
        extra.update({
            "task": task_for_logging
        })
        LOGGER.debug("Created task: %s", response.name, extra=extra)
        return MessageToDict(response._pb)
    
    async def create_task_v2(self, location, service_account_email, queue, url, payload, http_headers: Dict[str, str] = {}, schedule_time: datetime = None):
        from google.cloud import tasks_v2
        from google.protobuf.timestamp_pb2 import Timestamp
        from proto.message import MessageToDict

        extra = {
            "queue": queue,
            "url": url,
            "payload": payload,
            "http_headers": http_headers,
            "schedule_time": schedule_time
        }
        LOGGER.info(f"Creating task (v2) for queue: {queue}, url: {url}, payload: {payload}, schedule_time: {schedule_time}", extra=extra)

        client = tasks_v2.CloudTasksClient()
        project = self.project_id
        queue = queue
        location = location
        url = url
        service_account_email = service_account_email

        parent = client.queue_path(project, location, queue)

        httpRequest = {  
                        "http_method": tasks_v2.HttpMethod.POST,
                        'url': url,
                        "oidc_token": {"service_account_email": service_account_email},                            
                        "body":json.dumps(payload,cls=DateTimeEncoder).encode(),
                    }
        
        headers = {
            "Content-Type": "application/json"
        }

        if http_headers:
            headers.update(http_headers)

        httpRequest["headers"] = http_headers

        task = {
                    "http_request": httpRequest
                }
        
        if schedule_time:
            timestamp = Timestamp()
            timestamp.FromDatetime(schedule_time)
            task["schedule_time"] = timestamp

        response = client.create_task(parent=parent, task=task)
        # Create a copy of task for logging that excludes the bytes body
        task_for_logging = task.copy()
        task_for_logging["http_request"] = task["http_request"].copy()
        task_for_logging["http_request"]["body"] = json.dumps(payload, cls=DateTimeEncoder)  # Use JSON string instead of encoded bytes
        extra.update({
            "task": task_for_logging
        })
        LOGGER.debug("Created task (v2): %s", response.name, extra=extra)
        return MessageToDict(response._pb)