import asyncio
import json
import uuid
import aiormq


class CountNPVClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = ''
        self.futures = {}
        self.loop = asyncio.get_event_loop()

    async def connect(self, settings):
        self.connection = await aiormq.connect(settings.AMQP_URL)
        self.channel = await self.connection.channel()
        declare_ok = await self.channel.queue_declare(
            exclusive=True, auto_delete=True
        )
        await self.channel.basic_consume(declare_ok.queue, self.on_response)
        self.callback_queue = declare_ok.queue
        return self

    async def on_response(self, message: aiormq.abc.DeliveredMessage):
        future = self.futures.pop(message.header.properties.correlation_id)
        future.set_result(message.body)

    async def call(self, year, percent) -> float:
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()
        self.futures[correlation_id] = future
        await self.channel.basic_publish(
            json.dumps({'year': year, 'percent': percent}).encode('utf-8'),
            routing_key='rpc_queue',
            properties=aiormq.spec.Basic.Properties(
                content_type='application/json',
                correlation_id=correlation_id,
                reply_to=self.callback_queue,
            )
        )

        return await future
