from rejson import Path
from rejson.client import Client

class Cache:
    def __init__(self, json_client:Client):
        self.json_client = json_client

    async def get_chat_history(self, token: str,msg_id:int=None, count=None):
        if msg_id!=None:
            data = self.json_client.jsonget(
                str(token), f'$.messages[{msg_id}:{msg_id+count}]')
            return data
        else:
            data = self.json_client.jsonget(
                str(token), f'$.messages[*]')
            if data==None:
                return data
            if count!=None:
                return data[-count:]
            return data

    async def add_message_to_cache(self, token: str, source: str, message_data: dict):
        if source == "human":
            message_data['msg'] = "Human: " + (message_data['msg'])
        elif source == "bot":
            message_data['msg'] = "Bot: " + (message_data['msg'])
            # message_data['msg'] = (message_data['msg'])
        try:
            self.json_client.jsonarrappend(
                str(token), Path('.messages'), message_data)
        except Exception as err:
            print(err)
            