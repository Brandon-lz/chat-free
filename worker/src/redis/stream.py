'''
 * @Author: wl.liuzhao 
 * @Date: 2022-12-22 11:13:09 
 * @Last Modified by:   wl.liuzhao 
 * @Last Modified time: 2022-12-22 11:13:09 
 消费者实时拉取对话消息
'''
from aioredis.client import Redis
from aioredis.exceptions import ResponseError
from aioredis.exceptions import DataError

class StreamConsumer:
    def __init__(self, redis_client:Redis,groupname='chatgroup',consumer_name = 'worker01'):
        self.redis_client = redis_client
        self.groupname = groupname
        self.consumer_name= consumer_name
        
    
    async def init_consumer(self,stream_channel):
        """创建消费者组以及消费者

        Args:
            stream_channel (_type_): _description_
        """
        await self.redis_client.xtrim(stream_channel,10000) #设置队列大小
        # $代表消费者组从创建的时候开始读stream中的数据，0代表读取stream中所有的数据
        try:
            await self.redis_client.xgroup_create(stream_channel,groupname=self.groupname,mkstream=True,id='$')
        except ResponseError as err:
            if str(err)=='BUSYGROUP Consumer Group name already exists':
                print(f'消费者组{self.groupname}已经存在')
        
        # 相当于 self.redis_client.xgroup_createconsumer     但是不知道为啥并没有这个接口
        try:
            await self.redis_client.execute_command(*['XGROUP','CREATECONSUMER',stream_channel, self.groupname, self.consumer_name])
            print(f'消费者{self.consumer_name}成功上线')
        except DataError as err:
            print(err)
            raise
    

    async def consume_stream(self, count: int, block: int,  stream_channel, consume_not_ack=False):
        # 不使用消费者组
        # response = await self.redis_client.xread(
        #     streams={stream_channel:  '0-0'}, count=count, block=block)
        
        # 使用消费者组
        # > 代表读取group传递给当前消费者最新的数据，0代表读取group传给当前消费者所有未处理？的数据
        if consume_not_ack:     # 消费未被ack的数据，故障恢复时使用
            response = await self.redis_client.xpending(name=stream_channel,groupname=self.groupname)   # 读取未ack的消息
            if response.get('pending'):   # 如果读取到了
                # await self.redis_client.xclaim()   # 单消费者不能使用claim命令
                response = await self.redis_client.xrange(name=stream_channel,min=response.get('min'),max=response.get('min'))     # min==max 只获取一条消息
                # [(b'1678931917148-0', {b'fdeaeb71-3419-447f-86a7-b5c92f7c9b74': b' \xe5\xb8\xae\xe6\x88\x91\xe8\xb5\xb7\xe4\xb8\x80\xe4\xb8\xaa\xe8\x8b\xb1\xe6\x96\x87\xe5\x90\x8d\xe5\x90\xa7'})]
                response = [[stream_channel,[(response[0][0],response[0][1])]]]
                return response
            else:
                return []
        else:
            response = await self.redis_client.xreadgroup(groupname=self.groupname,consumername=self.consumer_name,streams={stream_channel:'>'},count=count,block=block)
        # >>>
        # [[b'message_channel_new', [(b'1675922129373-0', {b'5f31808f-19f5-4693-aaf6-e2ccf8341cb0': b'hi'})]]]
        # [[b'message_channel_new', [(b'1675922194051-0', {b'd8356b44-5ef2-4b31-81f0-60756f1ac65b': b'hi'})]]]
        return response

    async def ack_message(self,stream_channel,message_id):
        # 标记当前组中的某个消息为已处理，使用xreadgroup读取的时候将不会再次读到，实际上，只要xreadgroup的消息就不会被再读到
        await self.redis_client.xack(stream_channel,self.groupname,message_id)

    async def delete_message(self, stream_channel, message_id):
        # 删除消息
        await self.redis_client.xdel(stream_channel, message_id)
