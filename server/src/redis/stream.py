from aioredis.client import Redis


class StreamConsumer:
    def __init__(self, redis_client:Redis):
        self.redis_client = redis_client

    async def consume_stream(self, count: int, block: int,  stream_channel):
        # block ms  0代表一直阻塞
        response = await self.redis_client.xread(
            streams={stream_channel:  '0-0'}, count=count, block=block)
        return response

    async def delete_message(self, stream_channel, message_id):
        await self.redis_client.xdel(stream_channel, message_id)
    
    async def delete_channel(self,stream_channel):
        await self.redis_client.delete(stream_channel)
