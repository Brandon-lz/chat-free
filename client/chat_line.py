import flet as ft



# 用户生成自定义组件
class ChatCard(ft.UserControl):
    def __init__(self,text = "Music by Julie Gable. Lyrics by Sajkldjflajf;jflafafl ajflajfdljidney Stein .lajfdl ajflja fja;f sakdj flajdf \nadfafadsfwefava\n\r  adflja lfj dla jlfja;\
                                akdflajlfdjlkjf\t alkdfja adfsa\n adfakjfdls sadkfjalf\n adkflajlf asldf"
                                ,src_path='asset/bot.png',msg_id:int=0):
        super().__init__()
        self.msg_id = msg_id
        self.speaker_logo = ft.Image(
            src=src_path,
            width=96/2,
            height=96/2,
            # fit=ft.ImageFit.FILL,
        )
        self.speak_logo = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            height=96/2,
            controls=[
                self.speaker_logo,
            ]
        )
        self.speak_text = ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    # border_radius=5,
                    # bgcolor=ft.colors.BLUE_400,
                    content=ft.Column(
                        # expand=True,
                        controls=[
                            ft.Text(
                                text,
                                selectable=True,
                            ),
                        ]
                    )
                ),
            ]
        )
        self.blank_area = ft.Column(width=100)

    def build(self):
        return ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Row(
                    spacing=13,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        self.speak_logo,
                        self.speak_text,
                        # self.blank_area
                    ],
                )
            )
        )
        

class RobotChatLine(ChatCard):
    def __init__(self, text:str='''元宵节是中国传统的节日，也叫上元节、元夕节，在农历正月十五日过。它有着深厚的文化底蕴，是中华民族的 传统佳节。
二、元宵节传统习俗和风俗

1. 灯笼： 元宵节最重要的习俗之一就是悬挂彩灯，以此来表达对春天到来的喜庆。
2. 猜灯谜： 元宵节还有一个非常流行的传统习俗就是“猜灯谜”。
3. 吃汤圆： 元宵节吃汤圆也是一个重要的传统。
4. 踩高跷： 踩高跷又叫''',*args,**kwargs):
        super().__init__(text=text,*args,**kwargs)

class HumanChatLine(ChatCard):
    def __init__(self,text:str,*args,**kwargs):
        super().__init__(src_path='asset/boy.png',text=text,*args,**kwargs)
        self.speak_logo,self.speak_text = self.speak_text,self.speak_logo


# class RobotChatLine(ft.Row):
#     def __init__(self, text = "Music by Julie Gable. Lyrics by Sajkldjflajf;jflafafl ajflajfdljidney Stein .lajfdl ajflja fja;f sakdj flajdf \nadfafadsfwefava\n\r  adflja lfj dla jlfja;\
#                                 akdflajlfdjlkjf\t alkdfja adfsa\n adfakjfdls sadkfjalf\n adkflajlf asldf"
#                                 ,src_path='asset/bot.png',msg_id:int=0):
#         super().__init__()
#         self.expand = True
        
#         self.msg_id = msg_id
#         self.controls = [
#             RobotChatCard(text,msg_id=msg_id),
#             ft.Column(width=100),
#             ]


# class HumanChatLine(ft.Row):
#     def __init__(self, text = "Music by Julie Gable. Lyrics by Sajkldjflajf;jflafafl ajflajfdljidney Stein .lajfdl ajflja fja;f sakdj flajdf \nadfafadsfwefava\n\r  adflja lfj dla jlfja;\
#                                 akdflajlfdjlkjf\t alkdfja adfsa\n adfakjfdls sadkfjalf\n adkflajlf asldf"
#                                 ,src_path='asset/boy.png',msg_id:int=0):
#         super().__init__()
#         self.expand = True
        
#         self.msg_id = msg_id
#         self.controls = [
#             ft.Column(width=100),
#             HumanChatCard(text,msg_id=msg_id),
#             ]

