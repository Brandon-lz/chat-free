from aioredis.client import Redis

class Producer:
    def __init__(self, redis_client:Redis):
        self.redis_client = redis_client
        

    async def add_to_stream(self,  data: dict, stream_channel):
        # 先判断token还在不在
        try:
            msg_id = await self.redis_client.xadd(name=stream_channel, id="*", fields=data)
            
            print(f"Message id {msg_id} added to {stream_channel} stream")
            return msg_id

        except Exception as e:
            print(f"Error sending msg to stream => {e}")
