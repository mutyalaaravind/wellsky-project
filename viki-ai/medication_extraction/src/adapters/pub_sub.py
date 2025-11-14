from typing import Dict
import json
from google.cloud import pubsub_v1

from utils.custom_logger import getLogger

from utils.json import DateTimeEncoder

LOGGER = getLogger(__name__)

class GooglePubSubAdapter:

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient(
                publisher_options = pubsub_v1.types.PublisherOptions(
                enable_message_ordering=False,
            )
        )

    async def publish(
            self,            
            topic: str,
            message: Dict,
            ordering_key: str = None,
        ):

        topic_path = self.publisher.topic_path(self.project_id, topic)

        data = json.dumps(message, cls=DateTimeEncoder).encode("utf-8")

        LOGGER.debug("Sending message to project %s topic %s: %s", self.project_id, topic, data)

        if not ordering_key:
            future = self.publisher.publish(topic_path, data)
            return future.result()
        else:
            try:
                future = self.publisher.publish(topic_path, data, ordering_key=ordering_key)
                return future.result()
            except RuntimeError:
                # Resume publish on an ordering key that has had unrecoverable errors.
                self.publisher.resume_publish(topic_path, ordering_key)
                LOGGER.warning(f"Resumed publishing on ordering key: {ordering_key}")

        LOGGER.debug(f"Published message ID: {future.result()}")