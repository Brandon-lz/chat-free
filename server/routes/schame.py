
from pydantic import BaseModel


class ChatResponse(BaseModel):
    msg:str