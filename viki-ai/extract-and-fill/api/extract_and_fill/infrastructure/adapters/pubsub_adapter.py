from google.pubsub_v1 import PublisherAsyncClient,PubsubMessage
from extract_and_fill.infrastructure.ports import IMessageBusAdapter

class PubSubAdapter(IMessageBusAdapter):
    
    def __init__(self, project_id):
        self.publisher = PublisherAsyncClient()
        self.project_id = project_id

    async def publish(self, topic_path, message):
        # topic_path = self.publisher.topic_path(self.project_id, topic)
        # topic = self.publisher.create_topic(request={"name": topic_path})
        
        # TODO: Timeout
        await self.publisher.publish(
                topic=topic_path, messages=[PubsubMessage({"data":message.encode('utf-8')})]
            )
