# import flet as ft

# def main(page: ft.Page):
#     page.add(ft.Text(f"Initial route: {page.route}"))

#     def route_change(route):
#         page.add(ft.Text(f"New route: {route}"))

#     def go_store(e):
#         page.route = "/store"
#         page.update()

#     page.on_route_change = route_change
#     page.add(ft.ElevatedButton("Go to Store", on_click=go_store))

# ft.app(target=main, view=ft.WEB_BROWSER)

from datetime import datetime

print(datetime.now())

print(datetime.strftime(datetime.now(),f'%Y%m%d%H%M%S')+str(datetime.now()).split('.')[-1])


body = {
    "pid":2210,
    "type":"alipay",
    "out_trade_no":datetime.strftime(datetime.now(),f'%Y%m%d%H%M%S')+str(datetime.now()).split('.')[-1],
    "notify_url":"http://www.pay.com/notify_url.php",
    "name":"服务余额充值",
    "money":"1",
    "clientip":"10.30.24.13",
}

keys = list(body.keys())
keys.sort()
print(keys)

