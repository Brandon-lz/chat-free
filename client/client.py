import flet as ft
from chat_line import RobotChatLine,HumanChatLine
from memory_store import ClientData
from sider_bar import SiderBar
from user_logo import UserLogo
import requests
from rqest_funcs import *


class ChatArea(ft.Column):
    # 聊天区域，不包含输入框
    def __init__(self,page:ft.Page,client_data:ClientData):
        super().__init__()
        self.page = page
        self.client_data = client_data
        # self.height=800
        self.scroll = ft.ScrollMode.AUTO
        self.load_chat_history_bt = ft.FilledTonalButton('加载历史记录',width=400,height=30,on_click=self.clicked_chat_history)
        self.controls = [
            ft.Row(controls=[self.load_chat_history_bt],alignment=ft.MainAxisAlignment.CENTER),     # 显示历史记录按钮
        #     RobotChatLine(),
        #     HumanChatLine('12312'),
        #     RobotChatLine(),
        #     HumanChatLine('14535'),
        #     RobotChatLine(),
        #     HumanChatLine('12312'),
        #     RobotChatLine(),
        #     HumanChatLine('14535'),
        ]
        self.init_chat_history(count=4)
        # ! init函数里不能写update()

    def add_chatLine(self,role:str,text:str,msg_id=None,init=False):
        role = (role.strip(' '))
        if msg_id==None:
            if len(self.controls)==1:
                msg_id=0
            else:
                msg_id = self.controls[-1].msg_id+1
        if role=='Bot':
            chatline = RobotChatLine(text=text,msg_id=msg_id)
        elif role=='Human':
            chatline = HumanChatLine(text=text,msg_id=msg_id)
        else:
            print(111111111111)
            print(role)
            raise Exception('error')
        self.controls.append(chatline)
        if not init:
            self.update()
    
    def insert_chatLine(self,role,text,msg_id):
        role = (role.strip(' '))
        if msg_id==None:
            msg_id = self.controls[1].msg_id-1
        if role=='Bot':
            chatline = RobotChatLine(text=text,msg_id=msg_id)
        elif role=='Human':
            chatline = HumanChatLine(text=text,msg_id=msg_id)
        self.controls.insert(1,chatline)
    
    def init_chat_history(self,count:int=6):
        self.controls = [
            ft.Row(controls=[self.load_chat_history_bt],alignment=ft.MainAxisAlignment.CENTER),     # 显示历史记录按钮
        #     RobotChatLine(),
        #     HumanChatLine('12312'),
        #     RobotChatLine(),
        #     HumanChatLine('14535'),
        #     RobotChatLine(),
        #     HumanChatLine('12312'),
        #     RobotChatLine(),
        #     HumanChatLine('14535'),
        ]
        data = get_chat_history(count=count,token=self.client_data.crt_token)
        # print(data)
        if data==[] or data==None:
            return
        chatlenth = chat_history_lenth(token=self.client_data.crt_token)
        for i,d in enumerate(data):
            role,msg = d['msg'].split(':',maxsplit=1)
            self.add_chatLine(role=role,text=msg,msg_id=chatlenth-count+i,init=True)
    
    
    def load_chat_history(self,count:int=6):
        
        if len(self.controls)==1:
            self.init_chat_history(count)
            return
        
        min_msg_id = self.controls[1].msg_id
        if min_msg_id==0:
            return
        
        data = get_chat_history(token=self.client_data.crt_token,msg_id=min_msg_id,count=count,reverse=True)
        
        for i,d in enumerate(data[::-1]):
            role,msg = d['msg'].split(':',maxsplit=1)
            self.insert_chatLine(role=role,text=msg,msg_id=min_msg_id-1-i)

    def clicked_chat_history(self,e):
        self.load_chat_history(count=10)
        self.update()
        

# 直接继承组件
class TextInputer(ft.Column):
    def __init__(self,page:ft.Page,chat_area:ChatArea,client_data:ClientData,height=None,width=None):
        super().__init__()
        self.page = page
        self.chat_area = chat_area
        self.client_data = client_data
        self.text_field = ft.TextField(hint_text='按Ctrl+Enter发送',expand=True,multiline=True)
        self.height = height
        self.width = width
        self.send_bt = ft.FloatingActionButton('发送',on_click=self.send_clicked)

        self.progressbar = ft.ProgressBar(expand=True,color="amber", bgcolor="#eeeeee",visible=False)

        self.controls = [
            ft.Row(controls=[self.text_field,self.send_bt]),
            ft.Row(controls=[self.progressbar])
            ]
        
   
    def send_clicked(self,e):
        if self.text_field.value == '':
            return
        self.chat_area.add_chatLine(role='Human',text=self.text_field.value)
        text = self.text_field.value
        self.text_field.value = ''
        self.send_bt.disabled = True
        self.progressbar.visible = True

        self.update()

        res = self.send_request(data=text)
        self.chat_area.add_chatLine(role='Bot',text=res)
        self.send_bt.disabled = False
        self.progressbar.visible = False
        
        self.update()


    def send_request(self,data:str):
        headers = {}
        if self.client_data.username:
            headers.update({'Authorization': f'Bearer {self.client_data.jwt}'}) 
        res = requests.post(
            url='http://127.0.0.1:8091/chat_once',
            json={'token':self.client_data.crt_token,'data':data},
            headers=headers
        )
        if res.status_code==200:
            if self.client_data.jwt:
                self.client_data.jwt = res.headers['bearer']
            return res.json()['msg']
        else:
            raise Exception(res.text)

    
class ChatApp(ft.UserControl):
    # 聊天区域，包括聊天记录，聊天输入框
    def __init__(self,page:ft.Page,client_data:ClientData):
        super().__init__()
        self.page = page
        self.client_data = client_data
        self.chat_area = ChatArea(page,self.client_data)
        self.chat_inputer = TextInputer(self.page,self.chat_area,self.client_data,height=100,width=600)
        self.top_margin = 5
        self.bottom_margin = 5
                    
        # self.divider = ft.Divider(height=10,color=ft.colors.BACKGROUND)
        self.view = ft.Container(
            margin=ft.margin.only(top=self.top_margin,bottom=self.bottom_margin),
            # border=ft.border.only(top=50,bottom=50),
            # bgcolor=ft.colors.AMBER_400,
            content=ft.Column(
                expand=True,
                # height=page.height,    
                width=800,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.chat_area,
                    ft.Row(controls=[self.chat_inputer],alignment=ft.MainAxisAlignment.CENTER),
                ]
            )
        )
        
    def build(self):
        return self.view

    def resize(self):
        self.view.height = self.page.height
        # 重新计算消息记录框的大小
        self.chat_area.height = self.view.height-self.chat_inputer.height - self.top_margin - self.bottom_margin
        # self.view.update()
        self.page.update()
    
    def flush_area(self):
        self.chat_area = ChatArea(self.page,self.client_data)
        self.view.update()
        self.page.update()
        self.update()
        self.chat_area.update()
        





def create_app_topbar(page:ft.Page):
    page.appbar = ft.AppBar(
        toolbar_height=50,
        # leading=ft.Icon(ft.icons.PALETTE),
        # leading_width=40,
        title=ft.Text("ChatGPT"),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            # ft.IconButton(ft.icons.WB_SUNNY_OUTLINED),
            # ft.IconButton(ft.icons.FILTER_3),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Item 1"),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(text="Item 1"),
                    # ft.PopupMenuItem(
                    #     text="Checked item", checked=False, on_click=check_item_clicked
                    # ),
                ]
            ),
        ],
    )

def verify_email(page:ft.Page,token:str):
    try:
        rqest_verify_email(token)
        page.go('/register-success')
    except Exception as err:
        print('register-failure',err)
        page.go('/register-failure')
    # page.update
        





def main(page:ft.Page):
    # page.show_semantics_debugger = True     # debug 模式
    
    page.title = 'Chat App'
    # page.bgcolor = ft.colors.WHITE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    
    # / path
    client_data = ClientData(page)
    
    
    user_logo = UserLogo(page,client_data)

    sider_bar = SiderBar(page,client_data,user_logo)
    
    app = ChatApp(page,client_data)
    
    client_data.user_logo = user_logo
    client_data.sider_bar = sider_bar
    client_data.app = app
    
    
    
    def page_resize(e):
        # print("New page size:", page.window_width, page.window_height)
        # print("New page size:", page.width, page.height)
        app.resize()
        page.update()
    
    page.on_resize = page_resize
    
  
    def page_go_home(e):
        # page.views.clear()
        # page.views.append(view_root)
        page.go('/')
        
    
    view_root = ft.View(
        "/",
        controls=
        [
            ft.Row(
                expand=True,
                controls=[
                    sider_bar,
                    ft.VerticalDivider(width=1),
                    ft.Column(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[app]
                    ),
                ],
            )
        ],
        padding=ft.padding.only(left=10),
    )

    
    view_register_success  =  ft.View(
        "/register-success",
        controls=
        [
            ft.Row(
                expand=True,
                controls=[
                    # sider_bar,
                    # ft.VerticalDivider(width=1),
                    ft.Column(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[ft.Text('恭喜注册成功'),ft.TextButton('进入主页',
                                                                    on_click=page_go_home
                                                                    )]
                    ),
                ],
            )
        ],
        padding=ft.padding.only(left=10),
    )
    
    view_register_failure  =  ft.View(
        "/register-failure",
        controls=
        [
            ft.Row(
                expand=True,
                controls=[
                    # sider_bar,
                    # ft.VerticalDivider(width=1),
                    ft.Column(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[ft.Text('验证链接失效，请重新发送验证码'),ft.TextButton('进入主页',
                                                                    on_click=page_go_home
                                                                    )]
                    ),
                ],
            )
        ],
        padding=ft.padding.only(left=10),
    )
    
 
    
    def on_keyboard(e: ft.KeyboardEvent):
        # print(e.key)
        if e.key=='Enter' or e.key=='Numpad Enter':
            if sider_bar.user_logo.login_dig.open == True:
                sider_bar.user_logo.clicked_login(e=None)
            if e.ctrl:    
                app.chat_inputer.send_clicked(e=None)
        
        if e.key=='!':
            page.go('/register-success')
        
        # if e.key=='@':
            # page.go('/abc-11')
            # page.views.clear()
            # page.views.append(
            #     view_register_success
            # ),
            # page.update()
                        
        # page.add(
        #     ft.Text(
        #         f"Key: {e.key}, Shift: {e.shift}, Control: {e.ctrl}, Alt: {e.alt}, Meta: {e.meta}"
        #     )
        # )

    page.on_keyboard_event = on_keyboard
    
   
    def route_change(route):
        print('route change:',page.route)
        troute = ft.TemplateRoute(page.route)
        # print('router change:',troute.route)
        # print(troute.route)
        # if troute.match("/register/:token"):
        #     print("Book view ID:", troute.token)
        #     print(3333333333333)
        #     verify_email(token=troute.token)
        #     # 注册成功
        #     page.go("/register-success")
        #     page.views.clear()
        #     page.views.append(view_register_success)
        
        if troute.match("/register-success"):
            page.views.clear()
            page.views.append(
                view_register_success
            )
            
        elif troute.match("/register-failure"):
            page.views.clear()
            page.views.append(
                view_register_failure
            )
            page.update()
            
        # elif troute.match("/abc-11"):
        #     page.views.clear()
        #     page.views.append(
        #         ft.View('/abc',controls=[ft.Column(controls=[ft.Text(value='1243435')])])
        #     )
        # elif troute.match("/"):
        #     page.views.clear()
        #     page.views.append(view_root)
        else:
            # page.go("/")
            print('page.go("/")')
            page.views.clear()
            page.views.append(view_root)
            app.resize()       # 适配一下当前窗口
            page.update()

    page.on_route_change = route_change
    
    
    print(page.route)
    if '/verify' in page.route:
        print(page.route)
        token = str(page.route).split('/')[-1]
        print(token)
        verify_email(page,token)
        # page.go('/register-success')
        # page.update()
    
    else:
        page.go("/")

       
    
    
    


if __name__ == '__main__':

    ft.app(target=main,assets_dir='./asset',port=8092)


