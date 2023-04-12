import flet as ft
# from flet.control_event import ControlEvent
from memory_store import ClientData
import time
from rqest_funcs import register_user,get_user_account,recharge_by_manager,get_aim_user_balance
from decimal import Decimal

class RegisterForm(ft.UserControl):
    def __init__(self):
        super().__init__()
        
        
        # ft.Row(controls=[ft.Divider(),self.name_input],alignment=ft.MainAxisAlignment.CENTER)
        #             ft.Row(controls=[,ft.Divider(),self.email_input],alignment=ft.MainAxisAlignment.CENTER)
        
    def build(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
            ft.Column(ft.Text("姓名"),ft.Text('邮箱')),
            ft.Column(self.name_input,self.email_input)
        ])


from flet_core.control_event import ControlEvent
class ManagerDialg(ft.AlertDialog):
    def __init__(self,page:ft.Page,client_data:ClientData):
        """管理员工具  小窗口     

        Args:
            page (ft.Page): _description_
            client_data (ClientData): _description_
        """
        super().__init__()
       
        
        self.page = page
        self.client_data = client_data
           
        self.modal = False
        self.title = ft.Row(controls=[ft.Text('管理员工具')],alignment=ft.MainAxisAlignment.CENTER)
        
        def TextField_on_change(e:ControlEvent):
            text_control:ft.TextField = e.control
            text_control.error_text = ''
            text_control.update()
            
            
        # 输入组件
        self.email_inputer = ft.TextField(width=200,disabled=False,on_change=TextField_on_change)
        # self.password_inputer = ft.TextField(width=200)
        # self.button_create_user = ft.TextButton("创建新账号",on_click=self.create_user)
        self.balance = ft.Text(value='...',width=60)
        self.recharge_num = ft.TextField(hint_text='请输入充值金额\元',width=200)
        self.button_check_balance = ft.TextButton("查询余额",width=100, on_click=self.get_balance)
        self.button_recharge = ft.TextButton("充值", width=100, on_click=self.recharge)
        
        self.content=ft.Column(
                height=300,
                width=400,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(width=300,alignment=ft.MainAxisAlignment.START,controls=[ft.Column(controls=[ft.Text('用户邮箱')],horizontal_alignment=ft.CrossAxisAlignment.CENTER,width=100),self.email_inputer]),
                    # ft.Row(width=300,alignment=ft.MainAxisAlignment.START,controls=[
                    #     self.button_create_user,
                    #     self.password_inputer    
                    # ]),
                    ft.Divider(height=2),
                    ft.Row(width=300,alignment=ft.MainAxisAlignment.START,controls=[
                        self.button_check_balance,
                        self.balance,
                        
                    ]),
                    ft.Row(width=300,alignment=ft.MainAxisAlignment.START,controls=[
                        self.button_recharge,
                        self.recharge_num,
                    ]
                    )
                ]
            )
        self.actions=[
            # self.button_recharge,
            # ft.TextButton("关闭", on_click=self.close_current_dlg),
            
        ]
        self.actions_alignment=ft.MainAxisAlignment.CENTER
        self.on_dismiss=lambda e: self.update()

    def get_balance(self,e):
        # user_account = get_user_account(self.client_data.jwt)
        user_account = get_aim_user_balance(self.client_data.jwt,self.email_inputer.value)
        if user_account:
            self.balance.value = str(user_account['balance'])+' 元'
            self.update()
        else:
            self.balance.value = '...'
            self.email_inputer.error_text = '请输入正确的邮箱地址'
            self.email_inputer.update()
    
    def create_user(self,e):
        if self.password_inputer.value=='':
            self.password_inputer.error_text = '请输入密码再进行创建'
            self.password_inputer.update()
            return
        if len(self.password_inputer.value)<8:
            self.password_inputer.error_text = '密码长度不得小于8位'
            self.password_inputer.update()
            return
        
    
    def recharge(self,e):
        if self.email_inputer.value=='':
            self.email_inputer.error_text = '请输入被充值账号邮箱'
            self.email_inputer.update()
            return

        if self.recharge_num.value=='':
            self.recharge_num.error_text = '请输入充值金额'
            self.recharge_num.update()
            return

        try:
            Decimal(self.recharge_num.value)
        except:
            self.recharge_num.error_text = '无效的输入'
            self.recharge_num.update()
            return
    
        res = recharge_by_manager(self.client_data.jwt,self.email_inputer.value,Decimal(self.recharge_num.value))
        if res:
            self.recharge_num.value = ''
            self.recharge_num.error_text = '充值成功'
            self.balance.value = str(res['balance'])+' 元'
            self.recharge_num.update()
            self.balance.update()
        else:
            self.recharge_num.error_text = '充值失败'
            self.recharge_num.update()
            
    
 

class UserLogo(ft.UserControl):
    def __init__(self,page:ft.Page,client_data:ClientData):
        super().__init__()
        self.page = page
        self.client_data = client_data
        self.logo_image = ft.Image(src='asset/boy.png',width=96/2,height=96/2)
        
        self.username_text = ft.Text(value='未登录')
        if self.client_data.username:
            self.username_text.value= self.client_data.username
        
        
        self.manager_dlg = ManagerDialg(page,client_data)
            
        self.name_input_register = ft.TextField(width=250,disabled=False)
        self.email_input_register = ft.TextField(width=250,disabled=False)
        self.password_input_register = ft.TextField(width=250,password=True,disabled=False)
        self.password_input_register2 = ft.TextField(width=250,password=True,disabled=False)
        
        self.regester_dig =  ft.AlertDialog(
            modal=False,
            title=ft.Row(controls=[ft.Text('注册')],alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Column(
                height=300,
                width=400,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[ft.Text('用户名',width=60),self.name_input_register]),
                    ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[ft.Text('邮箱',width=60),self.email_input_register]),
                    ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[ft.Text('密码',width=60),self.password_input_register]),
                    ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[ft.Text('再次确认',width=60),self.password_input_register2]),
                    # ft.Row(controls=[ft.Icon(ft.icons.CHAT),ft.Icon(ft.icons.CHAT_BUBBLE_OUTLINE),ft.Icon(ft.icons.CHAT_BUBBLE_OUTLINE_ROUNDED)]),
                
                ]
            ),
            actions=[
                ft.TextButton("返回登录", on_click=self.turn_login),
                ft.TextButton("注册", on_click=self.clicked_register),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            on_dismiss=lambda e: self.update(),
        )
        
        
        def email_input_onchange(e):
            self.email_input_login.error_text = ''
            self.email_input_login.update()
            
        def password_input_onchange(e):
            self.password_input_login.error_text = ''
            self.password_input_login.update()
        
        self.email_input_login = ft.TextField(width=250,on_change=email_input_onchange)
        self.password_input_login = ft.TextField(width=250,password=True,on_change=password_input_onchange)
        
        
        
        self.login_dig = ft.AlertDialog(
            modal=False,
            title=ft.Row(controls=[ft.Text('登录')],alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Column(
                height=200,
                width=400,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(controls=[ft.Text("邮箱",width=50),ft.VerticalDivider(),self.email_input_login],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row(controls=[ft.Text('密码',width=50),ft.VerticalDivider(),self.password_input_login],alignment=ft.MainAxisAlignment.CENTER)
                ]
            ),
            actions=[
                ft.TextButton("登录", on_click=self.clicked_login),
                ft.TextButton("注册", on_click=self.turn_regester),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            on_dismiss=lambda e: self.update()
        )
        
        
        self.username_userinfo = ft.Text(self.client_data.username,width=250)
        self.email_userinfo =ft.Text(self.client_data.email,width=250)
        self.user_account = ft.Text(width=250)
        self.user_isverify = ft.Text(width=250)
        
        self.button_open_manager = ft.TextButton("管理员工具", on_click=self.turn_manager,visible=False)
        
        self.user_info_dig = ft.AlertDialog(
            modal=False,
            title=ft.Image(src='asset/boy.png',width=70,height=70),
            content=ft.Column(
                height=200,
                width=400,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(controls=[ft.Text("姓名"),ft.Divider(),self.username_userinfo],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row(controls=[ft.Text('邮箱'),ft.Divider(),self.email_userinfo],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row(controls=[ft.Text('余额'),ft.Divider(),self.user_account],alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row(controls=[ft.Text('验证'),ft.Divider(),self.user_isverify],alignment=ft.MainAxisAlignment.CENTER),
                ]
            ),
            actions=[
                ft.TextButton("注销", on_click=self.clicked_logout),
                self.button_open_manager
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            on_dismiss=lambda e: self.update()
        )
        

        
        self.pay_img = ft.Image(src='',width=380,height=380)
        
        self.pay_dlg = ft.AlertDialog(
            modal=False,
            title=ft.Text('请扫码支付'),
            content=ft.Column(
                height=400,
                width=400,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.pay_img
                ]
            ),
            actions=[
                ft.TextButton("关闭", on_click=self.close_current_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            on_dismiss=lambda e: self.update()
        )
        
        
        # 管理员工具        
        # 输入组件
        self.email_inputer = ft.TextField(width=250,disabled=False)
        self.balance = ft.Text(value='...',width=60)
        self.recharge_num = ft.TextField(hint_text='充值金额',width=100)
        # self.button_check_balance = ft.TextButton("查询余额", on_click=self.check_balance)
        # self.button_recharge = ft.TextButton("充值", on_click=self.recharge)
        
        # self.manager_dlg2 = ft.AlertDialog(
        #     modal=False,
        #     title=ft.Row(controls=[ft.Text('管理员工具')],alignment=ft.MainAxisAlignment.CENTER),
        #     content=ft.Column(
        #         height=300,
        #         width=400,
        #         alignment=ft.MainAxisAlignment.CENTER,
        #         controls=[
        #             ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[ft.Text('用户邮箱',width=60),self.email_inputer]),
        #             ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[
        #                 ft.Text('余额',width=60),
        #                 self.balance,
        #                 self.recharge_num,
        #                 # self.button_check_balance,
        #                 # self.button_recharge
        #             ]),
        #         ]
        #     ),
        #     actions=[
        #         # self.button_recharge,
        #         ft.TextButton("关闭", on_click=self.close_current_dlg),
                
        #     ],
        #     actions_alignment=ft.MainAxisAlignment.CENTER,
        #     # on_dismiss=lambda e: self.update(),
        # )
        
        
    def build(self):
        
        def on_hover(e):
            e.control.bgcolor = ft.colors.LIGHT_BLUE_100 if e.data == "true" else ft.colors.BACKGROUND
            e.control.update()
        
        return ft.Container(
            border_radius=8,
            width=110,
            height=110,
            content=ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.logo_image,
                    self.username_text
            ]),
            on_click=self.clicked_logo,
            on_hover=on_hover,
        )

   

    def clicked_login(self,e):
        # 提交数据，后端验证并返回jwt
        if self.client_data.login(email=self.email_input_login.value,password=self.password_input_login.value):
            self.close_current_dlg()
            self.password_input_login.value = ''
            self.client_data.flush_navication()
            self.client_data.flush_chatarea()
            self.update()
            return
        self.email_input_login.error_text = '用户名或密码错误'
        self.password_input_login.error_text = '用户名或密码错误'
        self.email_input_login.update()
        self.password_input_login.update()
    
    
    def click_pay(self,e):
        ...
        
            
    def open_login_dlg(self):
        self.page.dialog = self.login_dig
        self.login_dig.open = True
        self.page.update()
    
    def close_current_dlg(self):
        self.page.dialog.open = False
        self.page.update()
        time.sleep(0.1)

    
    def open_userinfo_dlg(self):
        self.email_userinfo.value = self.client_data.email
        self.username_userinfo.value = self.client_data.username
        self.user_isverify.value = '已验证' if self.client_data.is_verified else '未进行邮箱验证'
        user_account = get_user_account(self.client_data.jwt)
        self.user_account.value = f"{Decimal(user_account['balance']).quantize(Decimal('2.00'))} 元"
        
        if self.client_data.is_superuser:
            self.button_open_manager.visible = True
        
        self.page.dialog = self.user_info_dig
        self.page.dialog.open = True
        self.page.update()
        self.user_info_dig.update()
        

    # def close_userinfo_dlg(self):
    #     self.user_info_dig.open = False
    #     self.page.update()
    
    def open_regester_dlg(self):
        self.page.dialog = self.regester_dig
        self.regester_dig.open = True
        self.page.update()
    
    def open_manager_dlg(self):
        self.page.dialog = self.manager_dlg
        self.manager_dlg.open = True
        self.page.update()
    
    def open_pay_dlg(self):
        self.page.dialog = self.pay_dlg
        self.pay_dlg.open = True
        self.page.update()
    
    # def close_regester_dlg(self):
    #     self.regester_dig.open = False
    #     self.page.update()

    def clicked_logout(self,e):
        self.client_data.logout()
        self.close_current_dlg()
        self.client_data.app.chat_area.init_chat_history()
        self.client_data.app.chat_area.update()
        # self.user_info_dig.update()
        self.client_data.flush_navication()
        self.update()


    def clicked_register(self,e):
        if len(self.password_input_register.value)>=8:
            if self.password_input_register.value==self.password_input_register2.value:
                register_user(username=self.name_input_register.value,email=self.email_input_register.value,password=self.password_input_register.value)
                self.name_input_register.value = ''
                self.email_input_register.value = ''
                self.password_input_register.value = ''
                self.password_input_register2.value = ''
                self.turn_register_success()
                
            else:
                self.password_input_register.error_text = self.password_input_register2.error_text = '两次输入密码不一致'
                self.password_input_register.update()
                self.password_input_register2.update()
                
        else:
            self.password_input_register.error_text = '密码长度需大于8位'
            self.password_input_register.update()
            
    def turn_manager(self,e):
        self.close_current_dlg()
        self.open_manager_dlg()
        
    def turn_login(self,e):
        self.close_current_dlg()
        self.open_login_dlg()

    def turn_regester(self,e):
        self.close_current_dlg()
        self.open_regester_dlg()
        
    def turn_register_success(self):
        # self.close_current_dlg()
        self.turn_login(None)
    
    def turn_pay_dlg(self,e):
        self.close_current_dlg()
        self.open_pay_dlg()
        
        
    def clicked_logo(self,e):
        # 显示账户信息或登录窗口
        action = self.open_login_dlg if self.client_data.username==None else self.open_userinfo_dlg
        action()
        
    def login(self):
        ...
    
    
    def update(self):
        if self.client_data.username:
            self.username_text.value = self.client_data.username
        else:
            self.username_text.value = '未登录'
        return super().update()

