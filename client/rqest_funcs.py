import requests
from dotenv import load_dotenv
import os

load_dotenv()

def rquest_verify_token(email):
    res = requests.post(url=f"http://{os.environ['SERVER_HOST']}/auth/verify/request-verify-token",
                        json={'email':email}
                        )
    if res.status_code!=202:
        print(res.text)
        raise Exception('请求验证码失败')
    else:
        # print('已发送激活邮件')
        pass

def register_user(username,email,password):
    body = {
        "email": email,
        "password": password,
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "name": username,
        "descript": "user"
    }
    
    res = requests.post(
        url=f"http://{os.environ['SERVER_HOST']}/auth/register",
        json=body
    )
    if res.status_code==201:
        rquest_verify_token(email)
    elif res.status_code==400:
        print(res.json())
        # print('重复注册')
        
        

def rqest_verify_email(token)->dict:
    res = requests.post(
        url=f"http://{os.environ['SERVER_HOST']}/auth/verify/verify-bytoken",
        json={"uuid_token":token}
    )
    if res.status_code==200:
        return res.json()
    # elif res.status_code==400:
        # return Exception('邮箱验证失败')
    else:
        raise Exception('邮箱验证失败')

def get_or_create_user_tokens(jwt)->list:
    # 获取用户redis中的tokens，如果不存在则创建
    res = requests.get(
                url=f"http://{os.environ['SERVER_HOST']}/token",
                headers={'Authorization': f'Bearer {jwt}','Cache-Control':'no-cache'}
                )
    tokens = res.json()['tokens']
    return tokens

from decimal import Decimal
def get_user_account(jwt):
    # balance 是取2位小数的
    res = requests.get(
        url=f"http://{os.environ['SERVER_HOST']}/account/user-account",
        headers={'Authorization': f'Bearer {jwt}','Cache-Control':'no-cache'}
    )
    if res.status_code==200:
        result = res.json()
        result['balance'] = Decimal(value=result['balance']).quantize(Decimal('2.00'))
        return result
    else:
        raise Exception(res.text)
    
def get_aim_user_balance(super_jwt,aim_user_email):
    res = requests.get(
        url=f"http://{os.environ['SERVER_HOST']}/account/manager-get-user-account",
        params={'target_email':aim_user_email},
        headers={'Authorization': f'Bearer {super_jwt}','Cache-Control':'no-cache'}
    )
    if res.status_code==200:
        result = res.json()
        result['balance'] = Decimal(value=result['balance']).quantize(Decimal('2.00'))
        return result
    else:
        return None


def recharge_by_manager(super_jwt,aim_user_email,amount:Decimal):
    body = {
        "target_email": aim_user_email,
        "amount": str(amount)
    }
    res = requests.post(
        url=f"http://{os.environ['SERVER_HOST']}/account/recharge-by-manager",
        json=body,
        headers={'Authorization': f'Bearer {super_jwt}','Cache-Control':'no-cache'}
    )
    if res.status_code==200:
        return res.json()     # 返回目标账户信息
    return None
    

def get_chat_history(token,msg_id:int=None,count:int=None,reverse=True)->list:
    # websockets
    # requests.get(f"http://127.0.0.1:8091//chat_history?token={token}") as websocket:
    #     await websocket.send("Hello world!")
    #     return (await websocket.recv())
    parms = {'token':token,'count':count,'reverse':reverse}
    if msg_id!=None:
        parms.update({'msg_id':msg_id})
        
    res = requests.get(url=f"http://{os.environ['SERVER_HOST']}/chat_history",
                        params=parms,
                        headers={'Cache-Control':'no-cache'}
                        )
    if res.status_code==200:
        try:
            # print(res.text)
            # return eval(res.text)           # 第一次有报错
            return res.json()['msgs']
        except NameError:
            # raise
            return None
    else:
        raise Exception('获取聊天记录失败')



def chat_history_lenth(token):
    parms = {'token':token}
    res = requests.get(
        url=f"http://{os.environ['SERVER_HOST']}/chat_history_lenth",
        params=parms,
        headers={'Cache-Control':'no-cache'}
    )
    if res.status_code==200:
        return int(res.text)


def get_user_me(jwt)->dict:
    res = requests.get(
        url=f"http://{os.environ['SERVER_HOST']}/users/me",
        headers={'Authorization': f'Bearer {jwt}','Cache-Control':'no-cache'}
    )
    if res.status_code==200:
        return res.json()
    else:
        raise Exception(f'{get_user_me.__name__} failure')

import uuid

def add_chat_tag(jwt)->list:
    res = get_user_me(jwt)
    tokens :list= res['tokens']
    tokens.append(str(uuid.uuid4()))
    res = requests.patch(
        url=f"http://{os.environ['SERVER_HOST']}/users/me",
        json={'tokens':tokens},
        headers={'Authorization': f'Bearer {jwt}','Cache-Control':'no-cache'}
    )
    # tokens = res.json()['tokens']
    tokens = get_or_create_user_tokens(jwt)
    # res = requests.get
    return tokens

from datetime import datetime

import hashlib

def get_pay_img():
    body = {
            "pid":'2210',
            "type":"alipay",
            "out_trade_no":datetime.strftime(datetime.now(),f'%Y%m%d%H%M%S')+str(datetime.now()).split('.')[-1],
            "notify_url":"http://www.pay.com/notify_url.php",
            "name":"服务余额充值",
            "money":"1",
            "clientip":"10.30.24.13",
    }
    
    keys = list(body.keys())
    keys.sort()
    sign_str = ''
    for key in keys:
        sign_str += key + '=' + str(body[key]) + '&'
    sign_str = sign_str[:-1]
    print(sign_str)
    sign = hashlib.md5(sign_str.encode())
    body.update({
            "sign":sign.hexdigest(),
            "sign_type":"MD5"
        })
    print(body)
    res = requests.post(
        url='https://4ho.cn/mapi.php',
        json=body
    )
    
    print(res.status_code)
    print(res.text)
    print(res.json())



if __name__ == '__main__':
    get_pay_img()
    
    # sign = hashlib.md5(str(uuid.uuid4()).encode())
    # print(sign.digest())
    # print(len(sign.hexdigest()))
    # print(len(str(uuid.uuid4())))