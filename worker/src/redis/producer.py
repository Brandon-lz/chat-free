from aioredis.client import Redis

class Producer:
    def __init__(self, redis_client:Redis):
        self.redis_client = redis_client

    async def add_to_stream(self,  data: dict, stream_channel) -> bool:
        msg_id = await self.redis_client.xadd(name=stream_channel, id="*", fields=data)
        print(f"Message id {msg_id} added to {stream_channel} stream")
        await self.redis_client.expire(stream_channel,30*1)    #30s的超时
        return msg_id