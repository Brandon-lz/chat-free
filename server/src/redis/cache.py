from rejson.client import Client


class Cache:
    def __init__(self, json_client:Client):
        self.json_client = json_client

    async def get_chat_history(self, token: str,msg_id:int=None, count=None,reverse=False):
        if msg_id!=None:
            if reverse:
                start_index = msg_id-count
                start_index = 0 if start_index<0 else start_index
                data = self.json_client.jsonget(
                str(token), f'$.messages[{start_index}:{msg_id}]')
            else:
                data = self.json_client.jsonget(
                    str(token), f'$.messages[{msg_id}:{msg_id+count}]')
            return data
        else:
            data = self.json_client.jsonget(
                str(token), f'$.messages[*]')
            # self.json_client.jsonlen
            if data==None:
                return data
            if count!=None:
                return data[-count:]
            return data
    
    async def chat_history_lenth(self,token:str):
        data = self.json_client.jsonget(
                str(token), f'$.messages[*]')
        return len(data)


if __name__ == '__main__':
    import asyncio
    import os
    from dotenv import load_dotenv
    import aioredis
    
    
        
    load_dotenv()

    class Redis():
        def __init__(self):
            """initialize  connection """
            self.REDIS_URL = os.environ['REDIS_URL']
            self.REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
            self.REDIS_USER = os.environ['REDIS_USER']
            self.connection_url = f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_URL}"
            self.REDIS_HOST = os.environ['REDIS_HOST']
            self.REDIS_PORT = os.environ['REDIS_PORT']
            self.REDIS_DB = int(os.environ['REDIS_DB'])
            
        async def create_connection(self):
            self.connection = aioredis.from_url(
                self.connection_url, db=self.REDIS_DB)

            return self.connection
        
        def create_rejson_connection(self):
            self.redisJson = Client(host=self.REDIS_HOST,
                                    port=self.REDIS_PORT, decode_responses=True, username=self.REDIS_USER, password=self.REDIS_PASSWORD)

            return self.redisJson
    
    async def main():
        json_client = Redis().create_rejson_connection()
        cache = Cache(json_client)
        # data = await cache.get_chat_history("3ba992ad-075a-4032-8511-b10a47b1c396",msg_id=2,count=2)
        data = await cache.get_chat_history("3ba992ad-075a-4032-8511-b10a47b1c396",count=2)
        print(data)
        print(await cache.chat_history_lenth('3ba992ad-075a-4032-8511-b10a47b1c396'))
    
    asyncio.run(main())