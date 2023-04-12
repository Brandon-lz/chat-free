from fastapi import WebSocket
from typing import List
from aioredis.client import Redis
import asyncio

class ConnectionManager:
    def __init__(self,redis_conn,token):
        self.redis_conn:Redis = redis_conn
        self.token = token
        # self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # self.active_connections.append(websocket)
        # if await self.redis_conn.sadd('ws_client',token)==0:   # 添加到set中，用集合去计数
        #     print(f'发现重复的websocket连接{token}')
        await self.alive()    # 使用超时去计数
            
    async def alive(self,timeout=60):
        await self.redis_conn.setex(f'alive-{self.token}',timeout,'')
        
    async def get_all_alives(self)->List[bytes]:
        return await self.redis_conn.keys('alive-*')
        

    async def disconnect(self, websocket: WebSocket,token:str):
        try:
            await websocket.close()
        except:
            pass
        # try:
        #     self.active_connections.remove(websocket)
        # except:
        #     pass
        await self.redis_conn.srem('ws_client',token)
    
    async def is_connected(self,token)->int:
        """判断token用户当前是否在线

        Args:
            token (_type_): _description_

        Returns:
            int: 0不在线
        """
        return await self.redis_conn.sismember('ws_client',token)
    
    async def receive_text(self,websocket:WebSocket,timeout=None):
        if timeout:
            return await asyncio.wait_for(websocket.receive_text(), timeout=timeout)
        return await websocket.receive_text()

    async def send_personal_message(self, message: str, websocket: WebSocket):
        message.strip('Bot:')
        await websocket.send_text(message)
        