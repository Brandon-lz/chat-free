import motor.motor_asyncio
from beanie import PydanticObjectId
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from typing import Optional,List
import uuid

DATABASE_URL = "mongodb://192.168.222.129:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["chat-db3"]


from pydantic import Field

def init_tokens():
    return [str(uuid.uuid4())]

class User(BeanieBaseUser[PydanticObjectId]):
    name:Optional[str] = f'用户{str(uuid.uuid4())[-5:]}'
    # tokens:List[str] = [str(uuid.uuid4())]             # 在这里定义有可能会使用cache
    tokens:List[str] = Field(default_factory=init_tokens)
    descript:str
    email: str
 

async def get_user_db():
    yield BeanieUserDatabase(User)