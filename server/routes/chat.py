from fastapi import (
    APIRouter, 
    WebSocket,  
    Request, 
    BackgroundTasks, 
    HTTPException, 
    WebSocketDisconnect,
    Depends,
    Body
)
import uuid

from src.socket.connection import ConnectionManager
from src.socket.utils import get_token

from src.redis.producer import Producer
from src.redis.config import Redis

from src.schema.chat import Chat
from rejson import Path
from src.redis.stream import StreamConsumer
from src.redis.cache import Cache
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse

from user_app.users import current_active_user,user_or_not
from user_app.db import User
from user_app.users import refresh_jwt

        
from account_app.depends import get_account
from account_app.db import Account
from decimal import Decimal
from .schame import ChatResponse




chat = APIRouter()
redis = Redis()



templates = Jinja2Templates(directory="static/templates")


@chat.get("/", response_class=RedirectResponse)
async def read_item(request: Request):
    return RedirectResponse(url='http://127.0.0.1:8091/docs')



@chat.post("/token")
async def token_generator(request: Request,user:User = Depends(user_or_not)):
    token = str(uuid.uuid4())

    name = user.email if user else "temporary user"

    json_client = redis.create_rejson_connection()

    chat_session = Chat(
        token=token,
        messages=[],
        name=name
    )

    json_client.jsonset(str(token), Path.rootPath(), chat_session.dict())

    if user==None:
        redis_client = await redis.create_connection()      # 设置过期 失效时间
        await redis_client.expire(str(token), 60*60*12)

    return chat_session.dict()


@chat.get("/token")
async def get_tokens(request: Request,user:User = Depends(current_active_user),rj=Depends(refresh_jwt)):
    # 用户获取tokens  如果token在redis中不存在，则创建一个
    tokens = user.tokens
    json_client = redis.create_rejson_connection()
    
    for token in tokens:
        chat = json_client.jsonget(token)
        print(chat)
        if chat==None:
            chat_session = Chat(
                token=token,
                messages=[],
                name=user.name
            )
            # Store chat session in redis JSON with the token as key
            json_client.jsonset(str(token), Path.rootPath(), chat_session.dict())

    return {'tokens':tokens}



@chat.get("/refresh_token",description='当token失效的时候调用刷新')
async def refresh_token(request: Request, token: str):
    
    json_client = redis.create_rejson_connection()
    cache = Cache(json_client)
    data = await cache.get_chat_history(token)

    if data == None:
        raise HTTPException(
            status_code=400, detail="Session expired or does not exist")
    else:
        return data
    

        
@chat.get('/chat_history',description='msg_id存在则从该位置开始读取，不存在则返回最新的count条')
async def chat_history(request:Request,token:str,msg_id:int=None,count:int=None,reverse=False,rj = Depends(refresh_jwt)):
    json_client = redis.create_rejson_connection()
    cache = Cache(json_client)
    data = await cache.get_chat_history(token,msg_id,count,reverse)
    print(data)
    return {'msgs':data}

@chat.get('/chat_history_lenth',description='返回消息总数')
async def chat_history_lenth(request:Request,token:str,rj = Depends(refresh_jwt)):
    json_client = redis.create_rejson_connection()
    cache = Cache(json_client)
    return len(await cache.get_chat_history(token))



# @route   Websocket /chat
# @desc    Socket for chatbot
# @access  Public

chat_timeout = 1*60*5

from logs import logger

@chat.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(get_token),
                             ):
    
    redis_client = await redis.create_connection()
    manager = ConnectionManager(redis_conn=redis_client,token=token)
    await manager.connect(websocket)
    
    producer = Producer(redis_client)
    json_client = redis.create_rejson_connection()
    consumer = StreamConsumer(redis_client)
    
    continue_get_msg = False    # 是否拿多条消息
    try:
        while True:
            if not continue_get_msg:
                # data = await websocket.receive_text()
                data = await manager.receive_text(websocket,timeout=chat_timeout)     # 超时未收到消息则关闭连接
                await manager.alive(timeout=chat_timeout)
                print(await manager.get_all_alives())
                # # 测试ws通讯
                # await websocket.send_text(data)
                # continue
                # # 
                stream_data = {}
                stream_data[str(token)] = str(data)
                await producer.add_to_stream(stream_data, "message_channel_new")
                
            # 从redis中获取gpt回复
            response = await consumer.consume_stream(stream_channel=f"response_channel_new-{token}", block=0,count=1)
            print(response)
            for stream, messages in response:
                logger.info(f'message_data:{messages}')
                for message in messages:
                    # logger.info(type(message))
                    logger.debug(message[1])
                    # logger.debug(f'type:{type(message[1])}')
                    response_token = [k.decode('utf-8')
                                      for k, v in message[1].items()][0]
                    
                    # 校验一下token是否过期
                    if json_client.jsonget(name=token)==None:         # 这里是直接从对象中取的
                        # await consumer.delete_message(stream_channel="response_channel", message_id=message[0].decode('utf-8'))
                        await manager.send_personal_message('会话已经失效', websocket)
                        await manager.disconnect(websocket,token)
                        logger.error('会话已经失效')
                        return 
                    
                    
                    print(token)
                    print(response_token)
                    if token == response_token:
                        continue_get_msg = False
                        
                        message_content = message[1]
                        message_content = {k.decode('utf-8'):v.decode('utf-8') for k,v in message_content.items()}
                        # print('message_content_decode: ',message_content.values()[0])
                        # print(type(list(message_content.values())))
                        msg_dict = eval(list(message_content.values())[0])
                        print(msg_dict)
                        response_message = msg_dict['msg']
                        logger.debug(response_message)

                        await manager.send_personal_message(response_message, websocket)
                        await consumer.delete_message(stream_channel=f"response_channel_new-{token}", message_id=message[0].decode('utf-8'))
                    else:
                        logger(f'token:{token}-response_token:{response_token}')

    except WebSocketDisconnect:
        await manager.disconnect(websocket,token)
    finally:
        logger.info(f'session quit : {token}')
        await manager.disconnect(websocket,token)
        await consumer.delete_channel(stream_channel=f"response_channel_new-{token}")
        

@chat.post("/chat_once",response_model=ChatResponse)
async def chat_once(token: str = Body(default=None),data:str = Body(default=None),
    user:User=Depends(user_or_not),
    rj=Depends(refresh_jwt)
):
    if not user:
        return ChatResponse(msg='请点击左上角头像登录或注册')
    
    # 判断余额
    try:
        user_account :Account= await get_account(user)
    except Exception as err:
        return str(err)
    if user_account.balance==Decimal('0'):
        return ChatResponse(msg='余额不足，请充值\n充值链接：https://item.taobao.com/item.htm?spm=a1z10.3-c.0.0.d4ca6f23A8WdwR&id=675080497384')

    redis_client = await redis.create_connection()
    manager = ConnectionManager(redis_conn=redis_client,token=token)
    
    producer = Producer(redis_client)
    json_client = redis.create_rejson_connection()
    consumer = StreamConsumer(redis_client)
    
    try:
        await manager.alive(timeout=chat_timeout)
        stream_data = {}
        stream_data[str(token)] = str(data)
        await producer.add_to_stream(stream_data, "message_channel_new")
            
        # 从redis中获取gpt回复
        response = await consumer.consume_stream(stream_channel=f"response_channel_new-{token}", block=1000*100,count=1)
        print(response)
        for stream, messages in response:
            logger.info(f'message_data:{messages}')
            for message in messages:
                # logger.info(type(message))
                logger.debug(message[1])
                
                message_content = message[1]
                message_content = {k.decode('utf-8'):v.decode('utf-8') for k,v in message_content.items()}
                msg_dict = eval(list(message_content.values())[0])
                print(msg_dict)
                response_message = msg_dict['msg']
                logger.debug(response_message)
                await consumer.delete_message(stream_channel=f"response_channel_new-{token}", message_id=message[0].decode('utf-8'))
                
                # 扣除本次花费
                scale = 1.5       # 花费系数
                used_tokens = int(msg_dict['total_tokens'])
                unit_cost = 0.002*7/1000*scale
                user_account.balance = user_account.balance-Decimal(unit_cost*used_tokens)
                if (user_account.balance<0):user_account.balance=Decimal('0')
                # account.unit_cost = data.get('unit_cost') if data.get('unit_cost')!=None else account.unit_cost
                
                await user_account.save()
                
                return ChatResponse(msg=response_message)

    finally:
        logger.info(f'session quit : {token}')
        await consumer.delete_channel(stream_channel=f"response_channel_new-{token}")
        
