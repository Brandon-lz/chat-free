import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()


class GPT:
    def __init__(self):
        self.url = os.environ.get('MODEL_URL')
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('HUGGINFACE_INFERENCE_TOKEN')}"}
        self.payload = {
            "inputs": "",
            "parameters": {
                "return_full_text": False,
                "use_cache": False,
                "max_new_tokens": 25
            }

        }

    def query(self, input: str) -> str:
        self.payload["inputs"] = f"Human: {input} Bot:"
        data = json.dumps(self.payload)
        # proxy = '127.0.0.1:7890'
        # proxies = {
        #     "http": "http://%(proxy)s/" % {'proxy': proxy},
        #     "https": "http://%(proxy)s/" % {'proxy': proxy}
        # }
 
        response = requests.request(
            "POST", self.url, headers=self.headers, data=data)
        data = json.loads(response.content.decode("utf-8"))
        # print(11111111111)
        print(data)
        try:
            text = data[0]['generated_text']
            print('111111',text)
            res = str(text.split("Human:")[0]).strip("\n").strip()
        except KeyError:
            res = data['error']
        return res


if __name__ == "__main__":
    answer_str = GPT().query("Will artificial intelligence help humanity conquer the universe?")
    print(answer_str)
    
    