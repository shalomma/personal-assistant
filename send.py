import os
import json
import datetime
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage


class TextMessages:
    def __init__(self):
        self.cache = []

    def add(self, text: str, source: str = ''):
        self.cache.append(json.dumps({
            'source': source,
            'text': text,
            'time': str(datetime.datetime.now())
        }))


class Sender:
    NAMESPACE_CONNECTION_STR = os.getenv('NAMESPACE_CONNECTION_STR')
    QUEUE_NAME = "conversation"

    @staticmethod
    async def list_of_messages(sender, messages):
        bus_messages = [ServiceBusMessage(d) for d in messages.cache]
        await sender.send_messages(bus_messages)

    async def send(self, messages: TextMessages):
        # create a Service Bus client using the connection string
        async with ServiceBusClient.from_connection_string(
                conn_str=self.NAMESPACE_CONNECTION_STR,
                logging_enable=True) as servicebus_client:
            # Get a Queue Sender object to send messages to the queue
            sender = servicebus_client.get_queue_sender(queue_name=self.QUEUE_NAME)
            async with sender:
                # Send one message
                await self.list_of_messages(sender, messages)
        print('sent.')
