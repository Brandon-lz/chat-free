import os
from dotenv import load_dotenv
import openai
from logs import logger
from urllib3.exceptions import ProtocolError  

load_dotenv()

# openai.api_key = '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'
openai.api_key = os.environ.get('OpenAi_Token')


class GPT3:
    def query(self, input: str) -> str:
        input = input.replace('Human:','\nYou:')
        input = input.replace('Bot:','\nFriend:')
        input = input[1:]+'\nFriend:'
        
        logger.info('input:\n'+input)
        # openai
        response = openai.Completion.create(
            engine='text-davinci-003',          # 新版
            # model="text-davinci-003",
            # model="code-davinci-002",
            #   prompt="You: What have you been up to?\nFriend: Watching old movies.\nYou: Did you watch anything interesting?\nFriend:",
            # prompt="You: What have you been up to?\nFriend:",
            prompt = input,
            
            temperature=0.5,
            # max_tokens=400,
            # top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["You:"]
        )
            
        logger.info('---')
        logger.info('ouput:\n'+str(response))
        res:str = response.get('choices')[0].get('text')
        res = res.replace('Friend:','Bot:')
        return res

