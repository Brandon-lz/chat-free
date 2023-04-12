from beanie import PydanticObjectId
from fastapi_users import schemas
from typing import Optional,List

class UserRead(schemas.BaseUser[PydanticObjectId]):
    name:Optional[str]
    tokens:List[str]
    

import uuid
from pydantic import Field,PrivateAttr
class UserCreate(schemas.BaseUserCreate):
    name:Optional[str]
    # tokens:List[uuid.UUID] = PrivateAttr()
    descript:str
    
    # def __init__(self, **data):
    #     super().__init__(**data)
    #     # this could also be done with default_factory
    #     self.tokens = [str(uuid.uuid4())]


class UserUpdate(schemas.BaseUserUpdate):
    name:Optional[str]
    tokens:Optional[List[str]]
    descript:Optional[str]
    
        