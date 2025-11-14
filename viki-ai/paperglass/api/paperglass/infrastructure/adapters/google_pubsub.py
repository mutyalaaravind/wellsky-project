from typing import Dict
import json
from google.cloud import pubsub_v1

from paperglass.domain.util_json import DateTimeEncoder
from paperglass.infrastructure.ports import IMessagingPort

from paperglass.domain.context import Context

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

class GooglePubSubAdapter(IMessagingPort):

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient(
                publisher_options = pubsub_v1.types.PublisherOptions(
                enable_message_ordering=True,
            )
        )

    async def publish(
            self,            
            topic: str,
            message: Dict,
            ordering_key: str = None,
        ):

        with Context().getTracer().start_as_current_span("pubsub_publish") as span:

            topic_path = self.publisher.topic_path(self.project_id, topic)
            span.set_attribute("topic", topic)
            span.set_attribute("topicPath", topic_path)

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

            