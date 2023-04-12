# -*- coding: utf-8 -*-
# @Author   : LaiJiahao
# @Time     : 2022/12/8 16:44
# @File     : openai.py
# @Project  : openAI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class OpenAi:
    def __init__(self):
        # 使用的模型:功能最强大的 GPT-3
        self.model = "text-davinci-003"
        self.url = "https://api.openai.com/v1/completions"

    def get_answer(self,prompt,max_tokens,temperature):
        api_key = os.environ.get('OpenAi_Token')
        if max_tokens <= 4096 and temperature <= 0.9:
            if prompt:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }

                # Set up the API data
                data = {
                    "model": "text-davinci-003",
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
                # Make the API request
                response = requests.post(self.url, headers=headers, json=data)

                # Print the response

                answer = response.json()['choices'][0]['text']
            else:
                answer= "问题不能为空"
        else:
            answer = '你的max_tokens或temperature值过大！'
        return answer


if __name__ == '__main__':
    ai = OpenAi()
    print(ai.get_answer(prompt='你有没有女朋友',max_tokens=1000,temperature=0.7))
