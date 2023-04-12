import flet as ft
from typing import Union
import requests
from dotenv import load_dotenv
import os
from rqest_funcs import *
# from user_logo import UserLogo
# from sider_bar import SiderBar

load_dotenv()

class ClientData:
    
    def __init__(self,page:ft.Page) -> None:
        self.page = page
        self.is_superuser = False
        self.is_verified = False
        self.flush_user_data()
        self.crt_token = self.tokens[0]
        
        self.user_logo = None
        self.sider_bar = None
        self.app = None
    
    @property
    def jwt(self):
        return self._jwt
    
    @jwt.setter
    def jwt(self,jwt):
        self._jwt = jwt
        self.page.client_storage.set('user_jwt',jwt)
    
    def flush_user_data(self):
        self._jwt = self.page.client_storage.get('user_jwt')
        user = None if self.jwt==None else self.current_user()
        if user:
            self.username = user['name']
            self.email = user['email']
            self.is_superuser = user['is_superuser']
            self.is_verified = user['is_verified']
        else:
            self.username = None
            self.email = None
        self.tokens:list = self.get_tokens()
        self.crt_token = self.tokens[0]
        
        # print(self.jwt)
        
    def expire_user(self):
        # self.page.client_storage.remove('user_jwt')
        self.page.client_storage.clear()
        self.flush_user_data()
    

    def get_tokens(self)->list:
        try:
            if self.jwt:
                tokens = get_or_create_user_tokens(self.jwt)
                
            else:
                res = requests.post(
                    url=f"http://{os.environ['SERVER_HOST']}/token",
                )
                tokens = [res.json()['token']]
        except:
            raise Exception('聊天服务器出现故障')
        return tokens
    
    def login(self,email,password):
        res = requests.post(
            url=f"http://{os.environ['SERVER_HOST']}/auth/jwt/login",
            data={'username':email,'password':password},
        )
        
        if res.status_code==200:
            self.page.client_storage.set(key='user_jwt',value=res.json()['access_token'])
            self.flush_user_data()
            return True
        else:
            return False
    
    def logout(self):
        # self.page.client_storage.remove('user_jwt')
        self.page.client_storage.clear()
        self.flush_user_data()
        
        
    def current_user(self):
        if self.jwt:
            try:
                return get_user_me(self.jwt)
            except:
                self.expire_user()
        
        return None
    
    def update_user(self):
        res = requests.patch()
    
    def flush_chatarea(self):
        self.app.chat_area.init_chat_history()
        self.app.chat_area.update()
    
    def flush_navication(self):
        self.sider_bar.flush_navigation()
        self.sider_bar.update()
    