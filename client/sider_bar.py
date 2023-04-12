import flet as ft
from memory_store import ClientData
from user_logo import UserLogo
from rqest_funcs import *




class SiderBar(ft.UserControl):
    def __init__(self,page:ft.Page,client_data:ClientData,user_logo:UserLogo):
        super().__init__()
        self.page = page
        self.client_data = client_data
        # self.user_logo = UserLogo(self.page,self.client_data)
        self.user_logo = user_logo
        
        self.chat_tags = [
             ft.NavigationRailDestination(
                icon=ft.icons.CHAT_BUBBLE_OUTLINE, selected_icon=ft.icons.CHAT,
                label_content=ft.Text(f'会话{i+1}')
            ) for i,j in enumerate(self.client_data.tokens)
        ]
        
        
        self.no_login_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("当前未登录"),
            content=ft.Text("未登录用户只能使用一个聊天列表，且聊天记录可能在刷新或12小时后失效"),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=...,
        )
        
        

    def build(self):
        self.navigation = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            # extended=True,
            min_width=100,
            min_extended_width=400,
            leading=self.user_logo,
            group_alignment=-0.9,
            destinations=[
                *self.chat_tags,
                # ft.NavigationRailDestination(
                #     icon=ft.icons.CHAT_BUBBLE_OUTLINE, selected_icon=ft.icons.CHAT, label="First"
                # ),
            
                ft.NavigationRailDestination(
                    icon=ft.icons.ADD_OUTLINED,
                    selected_icon_content=ft.Icon(ft.icons.ADD),
                    label_content=ft.Text("add"),
                ),
            ],
            on_change=self.on_change,
        )
        return self.navigation
        
    def on_change(self,e):
        print("Selected destination:", e.control.selected_index)
        if e.control.selected_index==len(self.navigation.destinations)-1:        # 点击add
            if self.client_data.jwt!=None:
                self.on_click_add()
            else:
                self.open_dialog()
        else:
            self.client_data.crt_token = self.client_data.tokens[e.control.selected_index]
            # self.client_data.app.chat_area.init_chat_history()
            # self.client_data.app.chat_area.update()
            self.client_data.flush_chatarea()
                
    def flush_navigation(self):
        self.navigation.selected_index = 0
        self.client_data.crt_token = self.client_data.tokens[0]
        self.navigation.destinations = [
            *[
            ft.NavigationRailDestination(
                icon=ft.icons.CHAT_BUBBLE_OUTLINE, selected_icon=ft.icons.CHAT,
                label_content=ft.Text(f'会话{i+1}')
            ) for i,j in enumerate(self.client_data.tokens)
            ],
            ft.NavigationRailDestination(
                    icon=ft.icons.ADD_OUTLINED,
                    selected_icon_content=ft.Icon(ft.icons.ADD),
                    label_content=ft.Text("新增"),
                ),
        ]
        self.navigation.update()
        
            
    def on_click_add(self):
        self.client_data.tokens = add_chat_tag(self.client_data.jwt)
        self.client_data.crt_token = self.client_data.tokens[-1]
        self.navigation.destinations.insert(-1,ft.NavigationRailDestination(
                icon=ft.icons.CHAT_BUBBLE_OUTLINE, selected_icon=ft.icons.CHAT,
                label_content=ft.Text(f'会话{len(self.client_data.tokens)}')
            ))
        
        self.navigation.update()
        self.client_data.flush_chatarea()
        
    
    
    def open_dialog(self):
        self.page.dialog = self.no_login_dialog
        self.page.dialog.open = True
        self.page.update()

    def close_dialog(self,e):
        self.page.dialog.open=False
        self.page.update()
        
        