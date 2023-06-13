import tkinter as tk
import requests
import json
import os

class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("Mojang账户登录")

        self.label_username = tk.Label(master, text="用户名：")
        self.label_username.pack()

        self.entry_username = tk.Entry(master)
        self.entry_username.pack()

        self.label_password = tk.Label(master, text="密码：")
        self.label_password.pack()

        self.entry_password = tk.Entry(master, show="*")
        self.entry_password.pack()

        self.button_login = tk.Button(master, text="在线登录", command=self.online_login)
        self.button_login.pack()

        self.button_offline_login = tk.Button(master, text="离线登录", command=self.offline_login)
        self.button_offline_login.pack()

        self.button_external_login = tk.Button(master, text="外置登录", command=self.external_login)
        self.button_external_login.pack()

    def online_login(self):
        # 获取用户名和密码
        username = self.entry_username.get()
        password = self.entry_password.get()

        # 构造POST请求的数据
        payload = {
            "agent": {
                "name": "Minecraft",
                "version": 1
            },
            "username": username,
            "password": password,
            "requestUser": "true"
        }
        headers = {
            "Content-Type": "application/json"
        }

        # 发送POST请求，获取响应
        response = requests.post("https://authserver.mojang.com/authenticate", data=json.dumps(payload), headers=headers)

        # 解析响应的JSON数据
        response_json = response.json()

        # 判断是否登录成功
        if "accessToken" in response_json:
            # 输出响应结果中的access_token
            access_token = response_json["accessToken"]
            print("登录成功，access_token为：", access_token)

            # 将access_token写入离线登录文件
            offline_file_path = os.path.join(os.getcwd(), "offline_token.txt")
            with open(offline_file_path, "w") as f:
                f.write(access_token)
        else:
            # 输出错误信息
            error_message = response_json["errorMessage"]
            print("登录失败，错误信息：", error_message)

    def offline_login(self):
        # 获取用户名
        username = self.entry_username.get()

        # 构造离线登录文件路径
        offline_file_path = os.path.join(os.getcwd(), "offline_token.txt")

        # 判断离线登录文件是否存在
        if os.path.exists(offline_file_path):
            # 读取离线登录文件中的access_token
            with open(offline_file_path, "r") as f:
                access_token = f.read()

            # 输出access_token
            print("离线登录成功，access_token为：", access_token)
        else:
            # 输出错误信息
            print("离线登录失败，离线登录文件不存在或已被删除！")

    def external_login(self):
        # 获取用户名和access_token
        username = self.entry_username.get()
        access_token = self.entry_password.get()

        # 判断access_token是否为空
        if access_token:
            # 构造离线登录文件路径
            offline_file_path = os.path.join(os.getcwd(), "offline_token.txt")

            # 将access_token写入离线登录文件
            with open(offline_file_path, "w") as f:
                f.write(access_token)

            # 输出access_token
            print("外置登录成功，access_token为：", access_token)
        else:
            # 输出错误信息
            print("外置登录失败，access_token不能为空！")

if __name__ == '__main__':
    root = tk.Tk()
    login_window = LoginWindow(root)
    root.mainloop()
